package com.lxmusic.tv.script

/**
 * 洛雪音源运行时桥（参考 lx-music-mobile 的 user-api-preload.js）
 *
 * 在 QuickJS 引擎中为音源脚本提供 globalThis.lx 运行时：
 * - lx.EVENT_NAMES / lx.request / lx.on / lx.send / lx.utils
 * - 异步 HTTP 请求队列：JS 侧登记回调 -> nativeCall 发请求 -> Java 完成 -> __lx_on_response__ 注入
 * - setTimeout / clearTimeout（经 nativeCall schedule_timer 由引擎循环触发）
 * - __lx_dispatch__：Java 派发 request 事件，返回 holder{done,value,error}，Java 侧轮询等待
 *
 * 注意：本文件为纯 JS 文本，不要使用 Kotlin 模板语法（${}）或三引号嵌套。
 */
object QuickJSPreload {
    val SCRIPT: String = """
(function () {
  'use strict';

  // ===== 事件名 =====
  var EVENT_NAMES = {
    request: 'request',
    inited: 'inited',
    updateAlert: 'updateAlert'
  };

  // ===== JS -> Java 桥 =====
  // __lx_native_call__(action, dataJson) 由 Java 层注册；
  // 同步型 action（aes_encrypt/md5）返回结果字符串，异步型返回 null
  function nativeCall(action, data) {
    var payload = (typeof data === 'string') ? data : JSON.stringify(data || {});
    if (typeof __lx_native_call__ === 'function') {
      return __lx_native_call__(action, payload);
    }
    return null;
  }

  // ===== 异步 HTTP 请求队列 =====
  var requestQueue = {};
  var requestSeq = 0;

  function lxRequest(url, options, callback) {
    var opts = options || {};
    var key = 'r' + (++requestSeq);
    if (typeof callback === 'function') {
      requestQueue[key] = callback;
    }
    nativeCall('request', {
      key: key,
      url: String(url),
      method: (opts.method || 'get'),
      headers: opts.headers || {},
      body: opts.body || '',
      timeout: opts.timeout || 0
    });
    // 返回取消函数（简化实现：不真正取消）
    return function () {};
  }

  // ===== 通用 Web API：fetch / Response-like =====
  // 使用同一個受控 HTTP bridge，讓非洛雪腳本可採用常見 fetch 介面。
  // 不暴露任意 socket；請求仍由 Android HttpClient 統一執行與控管。
  globalThis.fetch = function (input, init) {
    var opts = init || {};
    var url = (typeof input === 'string') ? input : (input && input.url) || String(input);
    var method = opts.method || (input && input.method) || 'GET';
    var headers = opts.headers || (input && input.headers) || {};
    var body = (opts.body !== undefined) ? opts.body : '';
    return new Promise(function (resolve, reject) {
      lxRequest(url, {
        method: method,
        headers: headers,
        body: body,
        timeout: opts.timeout || 0
      }, function (err, response, responseBody) {
        if (err) {
          reject(new Error(String(err)));
          return;
        }
        var textBody = (typeof responseBody === 'string')
          ? responseBody
          : JSON.stringify(responseBody == null ? '' : responseBody);
        var responseHeaders = response && response.headers ? response.headers : {};
        resolve({
          ok: !!(response && response.statusCode >= 200 && response.statusCode < 300),
          status: response ? Number(response.statusCode) || 0 : 0,
          statusText: response ? (response.statusMessage || '') : '',
          url: url,
          headers: {
            get: function (name) {
              var target = String(name).toLowerCase();
              var keys = Object.keys(responseHeaders);
              for (var i = 0; i < keys.length; i++) {
                if (keys[i].toLowerCase() === target) return String(responseHeaders[keys[i]]);
              }
              return null;
            },
            forEach: function (callback) {
              Object.keys(responseHeaders).forEach(function (key) {
                callback(String(responseHeaders[key]), key);
              });
            }
          },
          text: function () { return Promise.resolve(textBody); },
          json: function () {
            try { return Promise.resolve(JSON.parse(textBody)); }
            catch (e) { return Promise.reject(e); }
          },
          clone: function () { return this; }
        });
      });
    });
  };

  // ===== 通用 Web API：非同步 XMLHttpRequest =====
  // 僅支援非同步請求；底層仍使用 Android HTTP bridge。
  function LXXMLHttpRequest() {
    this.readyState = 0;
    this.status = 0;
    this.statusText = '';
    this.responseText = '';
    this.response = null;
    this.responseType = '';
    this.timeout = 0;
    this.withCredentials = false;
    this.onreadystatechange = null;
    this.onloadstart = null;
    this.onprogress = null;
    this.onload = null;
    this.onerror = null;
    this.ontimeout = null;
    this.onabort = null;
    this.onloadend = null;
    this._method = 'GET';
    this._url = '';
    this._headers = {};
    this._responseHeaders = {};
    this._sendFlag = false;
    this._aborted = false;
    this._listeners = {};
  }

  LXXMLHttpRequest.UNSENT = 0;
  LXXMLHttpRequest.OPENED = 1;
  LXXMLHttpRequest.HEADERS_RECEIVED = 2;
  LXXMLHttpRequest.LOADING = 3;
  LXXMLHttpRequest.DONE = 4;

  LXXMLHttpRequest.prototype.addEventListener = function (type, listener) {
    if (typeof listener !== 'function') return;
    (this._listeners[type] || (this._listeners[type] = [])).push(listener);
  };
  LXXMLHttpRequest.prototype.removeEventListener = function (type, listener) {
    var list = this._listeners[type] || [];
    this._listeners[type] = list.filter(function (item) { return item !== listener; });
  };
  LXXMLHttpRequest.prototype._emit = function (type) {
    var event = { type: type, target: this, currentTarget: this };
    var handler = this['on' + type];
    if (typeof handler === 'function') {
      try { handler.call(this, event); } catch (e) {}
    }
    (this._listeners[type] || []).slice().forEach(function (listener) {
      try { listener.call(this, event); } catch (e) {}
    }, this);
  };
  LXXMLHttpRequest.prototype._change = function (state) {
    this.readyState = state;
    this._emit('readystatechange');
  };
  LXXMLHttpRequest.prototype.open = function (method, url, async) {
    if (async === false) throw new Error('Synchronous XMLHttpRequest is not supported');
    if (this._sendFlag) throw new Error('InvalidStateError');
    this._method = String(method || 'GET').toUpperCase();
    this._url = String(url);
    this.status = 0;
    this.statusText = '';
    this.responseText = '';
    this.response = null;
    this._headers = {};
    this._responseHeaders = {};
    this._aborted = false;
    this._sendFlag = false;
    this._change(LXXMLHttpRequest.OPENED);
  };
  LXXMLHttpRequest.prototype.setRequestHeader = function (name, value) {
    if (this.readyState !== LXXMLHttpRequest.OPENED || this._sendFlag) throw new Error('InvalidStateError');
    var key = String(name);
    this._headers[key] = this._headers[key] ? this._headers[key] + ', ' + String(value) : String(value);
  };
  LXXMLHttpRequest.prototype.getResponseHeader = function (name) {
    if (this.readyState < LXXMLHttpRequest.HEADERS_RECEIVED) return null;
    var target = String(name).toLowerCase();
    var keys = Object.keys(this._responseHeaders);
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].toLowerCase() === target) return String(this._responseHeaders[keys[i]]);
    }
    return null;
  };
  LXXMLHttpRequest.prototype.getAllResponseHeaders = function () {
    if (this.readyState < LXXMLHttpRequest.HEADERS_RECEIVED) return '';
    return Object.keys(this._responseHeaders).map(function (key) {
      return key + ': ' + this._responseHeaders[key] + '\\r\\n';
    }, this).join('');
  };
  LXXMLHttpRequest.prototype.send = function (body) {
    if (this.readyState !== LXXMLHttpRequest.OPENED || this._sendFlag) throw new Error('InvalidStateError');
    this._sendFlag = true;
    this._emit('loadstart');
    var self = this;
    lxRequest(this._url, {
      method: this._method,
      headers: this._headers,
      body: body == null ? '' : body,
      timeout: this.timeout || 0
    }, function (err, response, responseBody) {
      if (self._aborted) return;
      self._sendFlag = false;
      if (err) {
        if (String(err).toLowerCase().indexOf('timeout') >= 0) self._emit('timeout');
        else self._emit('error');
        self._change(LXXMLHttpRequest.DONE);
        self._emit('loadend');
        return;
      }
      self._responseHeaders = response && response.headers ? response.headers : {};
      self._change(LXXMLHttpRequest.HEADERS_RECEIVED);
      self._change(LXXMLHttpRequest.LOADING);
      self.status = response ? Number(response.statusCode) || 0 : 0;
      self.statusText = response ? (response.statusMessage || '') : '';
      self.responseText = typeof responseBody === 'string'
        ? responseBody : JSON.stringify(responseBody == null ? '' : responseBody);
      try {
        self.response = self.responseType === 'json'
          ? JSON.parse(self.responseText) : self.responseText;
      } catch (e) {
        self.response = null;
      }
      self._change(LXXMLHttpRequest.DONE);
      self._emit('load');
      self._emit('loadend');
    });
  };
  LXXMLHttpRequest.prototype.abort = function () {
    if (!this._sendFlag && this.readyState === LXXMLHttpRequest.UNSENT) return;
    this._aborted = true;
    this._sendFlag = false;
    this.status = 0;
    this.response = null;
    this.responseText = '';
    this._change(LXXMLHttpRequest.UNSENT);
    this._emit('abort');
    this._emit('loadend');
  };
  globalThis.XMLHttpRequest = LXXMLHttpRequest;

  // ===== 通用 Web API：URL / URLSearchParams =====
  function LXURLSearchParams(init) {
    this._items = [];
    var self = this;
    if (init instanceof LXURLSearchParams) {
      init._items.forEach(function (pair) { self._items.push([pair[0], pair[1]]); });
    } else if (typeof init === 'string') {
      var query = init.charAt(0) === '?' ? init.slice(1) : init;
      if (query) query.split('&').forEach(function (part) {
        if (!part) return;
        var index = part.indexOf('=');
        var key = index < 0 ? part : part.slice(0, index);
        var value = index < 0 ? '' : part.slice(index + 1);
        try { key = decodeURIComponent(key.replace(/\\+/g, ' ')); } catch (e) {}
        try { value = decodeURIComponent(value.replace(/\\+/g, ' ')); } catch (e) {}
        self._items.push([key, value]);
      });
    } else if (Array.isArray(init)) {
      init.forEach(function (pair) {
        if (pair && pair.length >= 2) self.append(pair[0], pair[1]);
      });
    } else if (init && typeof init === 'object') {
      Object.keys(init).forEach(function (key) { self.append(key, init[key]); });
    }
  }
  LXURLSearchParams.prototype.append = function (name, value) {
    this._items.push([String(name), String(value)]);
  };
  LXURLSearchParams.prototype.delete = function (name) {
    name = String(name);
    this._items = this._items.filter(function (pair) { return pair[0] !== name; });
  };
  LXURLSearchParams.prototype.get = function (name) {
    name = String(name);
    for (var i = 0; i < this._items.length; i++) if (this._items[i][0] === name) return this._items[i][1];
    return null;
  };
  LXURLSearchParams.prototype.getAll = function (name) {
    name = String(name);
    return this._items.filter(function (pair) { return pair[0] === name; }).map(function (pair) { return pair[1]; });
  };
  LXURLSearchParams.prototype.has = function (name) {
    name = String(name);
    return this._items.some(function (pair) { return pair[0] === name; });
  };
  LXURLSearchParams.prototype.set = function (name, value) {
    name = String(name); value = String(value);
    var found = false;
    var next = [];
    this._items.forEach(function (pair) {
      if (pair[0] !== name) next.push(pair);
      else if (!found) { next.push([name, value]); found = true; }
    });
    if (!found) next.push([name, value]);
    this._items = next;
  };
  LXURLSearchParams.prototype.sort = function () {
    this._items.sort(function (a, b) { return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0; });
  };
  LXURLSearchParams.prototype.forEach = function (callback, thisArg) {
    this._items.slice().forEach(function (pair) { callback.call(thisArg, pair[1], pair[0], this); }, this);
  };
  LXURLSearchParams.prototype.toString = function () {
    return this._items.map(function (pair) {
      return encodeURIComponent(pair[0]).replace(/%20/g, '+') + '=' +
        encodeURIComponent(pair[1]).replace(/%20/g, '+');
    }).join('&');
  };
  if (typeof globalThis.URLSearchParams !== 'function') globalThis.URLSearchParams = LXURLSearchParams;

  function LXURL(input, base) {
    if (!(this instanceof LXURL)) throw new TypeError("URL constructor requires 'new'");
    var raw = String(input);
    if (base) {
      var baseUrl = base instanceof LXURL ? base.href : String(base);
      if (!/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(raw)) {
        if (raw.slice(0, 2) === '//') {
          var scheme = baseUrl.match(/^([a-zA-Z][a-zA-Z0-9+.-]*:)/);
          raw = (scheme ? scheme[1] : 'https:') + raw;
        } else if (raw.charAt(0) === '/') {
          var origin = baseUrl.match(/^([a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^/]+)/);
          if (!origin) throw new TypeError('Invalid base URL');
          raw = origin[1] + raw;
        } else {
          var prefix = baseUrl.replace(/[?#].*$/, '');
          raw = prefix.slice(0, prefix.lastIndexOf('/') + 1) + raw;
        }
      }
    }
    var match = raw.match(/^([a-zA-Z][a-zA-Z0-9+.-]*:)\\/\\/([^/?#]*)([^?#]*)(?:\\?([^#]*))?(?:#(.*))?$/);
    if (!match) throw new TypeError('Invalid URL: ' + raw);
    this.protocol = match[1].toLowerCase();
    var authority = match[2];
    var at = authority.lastIndexOf('@');
    this.username = at >= 0 ? authority.slice(0, at).split(':')[0] : '';
    this.password = at >= 0 && authority.slice(0, at).indexOf(':') >= 0
      ? authority.slice(0, at).slice(authority.slice(0, at).indexOf(':') + 1) : '';
    var hostPort = at >= 0 ? authority.slice(at + 1) : authority;
    var hostMatch = hostPort.match(/^([^:]+)(?::(\\d+))?$/);
    if (!hostMatch) throw new TypeError('Invalid URL authority');
    this.hostname = hostMatch[1].toLowerCase();
    this.port = hostMatch[2] || '';
    this.host = this.hostname + (this.port ? ':' + this.port : '');
    this.origin = this.protocol + '//' + this.host;
    this.pathname = match[3] || '/';
    this.search = match[4] ? '?' + match[4] : '';
    this.hash = match[5] ? '#' + match[5] : '';
    this.searchParams = new globalThis.URLSearchParams(this.search);
    this._sync = function () {
      this.search = this.searchParams.toString() ? '?' + this.searchParams.toString() : '';
      this.href = this.origin + this.pathname + this.search + this.hash;
    };
    this._sync();
  }
  Object.defineProperty(LXURL.prototype, 'href', {
    get: function () { return this._href || ''; },
    set: function (value) { this._href = String(value); }
  });
  LXURL.prototype.toString = function () { return this.href; };
  LXURL.prototype.toJSON = function () { return this.href; };
  if (typeof globalThis.URL !== 'function') globalThis.URL = LXURL;

  // ===== 定时器 =====
  var timerCallbacks = {};
  var timerSeq = 0;

  function lxSetTimeout(callback, delay) {
    var id = ++timerSeq;
    timerCallbacks[id] = callback;
    nativeCall('schedule_timer', { id: id, delay: Math.max(0, Number(delay) || 0) });
    return id;
  }

  function lxClearTimeout(id) {
    delete timerCallbacks[id];
    nativeCall('clear_timer', { id: id });
  }

  globalThis.setTimeout = lxSetTimeout;
  globalThis.clearTimeout = lxClearTimeout;

  // ===== 事件注册 =====
  var events = {};
  var isInited = false;
  var isShowedUpdateAlert = false;

  function lxOn(eventName, handler) {
    if (eventName === EVENT_NAMES.request) {
      events.request = handler;
      return Promise.resolve();
    }
    return Promise.reject(new Error('The event is not supported: ' + eventName));
  }

  function lxSend(eventName, data) {
    if (eventName === EVENT_NAMES.inited) {
      if (isInited) return Promise.resolve();
      isInited = true;
      nativeCall('inited', data || {});
      return Promise.resolve();
    }
    if (eventName === EVENT_NAMES.updateAlert) {
      if (isShowedUpdateAlert) return Promise.resolve();
      isShowedUpdateAlert = true;
      nativeCall('update_alert', data || {});
      return Promise.resolve();
    }
    return Promise.reject(new Error('The event is not supported: ' + eventName));
  }

  // ===== 洛雪兼容 utils（参考 lx-music-mobile user-api-preload.js）=====
  // 六音等混淆源在启用阶段就调用 utils.buffer.from / utils.crypto.aesEncrypt，
  // utils 缺失（空对象）会直接崩在脚本自举（cannot read property 'from' of undefined）。
  // buffer 纯 JS 实现（UTF-8/hex/base64）；AES/MD5 经 nativeCall 走 Java（Cipher/MessageDigest）。

  // UTF-8 字节数组 -> 字符串（手写循环，避免 apply 大数组爆栈）
  function bytesToString(bytes) {
    var result = '';
    var i = 0;
    while (i < bytes.length) {
      var byte = bytes[i];
      if (byte < 128) {
        result += String.fromCharCode(byte);
        i++;
      } else if (byte >= 192 && byte < 224) {
        result += String.fromCharCode(((byte & 31) << 6) | (bytes[i + 1] & 63));
        i += 2;
      } else {
        result += String.fromCharCode(((byte & 15) << 12) | ((bytes[i + 1] & 63) << 6) | (bytes[i + 2] & 63));
        i += 3;
      }
    }
    return result;
  }

  // 字符串 -> UTF-8 字节数组
  function stringToBytes(inputString) {
    var bytes = [];
    for (var i = 0; i < inputString.length; i++) {
      var charCode = inputString.charCodeAt(i);
      if (charCode < 128) {
        bytes.push(charCode);
      } else if (charCode < 2048) {
        bytes.push((charCode >> 6) | 192);
        bytes.push((charCode & 63) | 128);
      } else {
        bytes.push((charCode >> 12) | 224);
        bytes.push(((charCode >> 6) & 63) | 128);
        bytes.push((charCode & 63) | 128);
      }
    }
    return bytes;
  }

  var B64_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

  // base64 -> 字节数组（纯 JS，QuickJS 无 atob）
  function base64ToBytes(b64) {
    b64 = String(b64).replace(/[^A-Za-z0-9+/=]/g, '');
    var bytes = [];
    var buffer = 0;
    var bits = 0;
    for (var i = 0; i < b64.length; i++) {
      if (b64[i] === '=') break;
      var val = B64_CHARS.indexOf(b64[i]);
      if (val < 0) continue;
      buffer = (buffer << 6) | val;
      bits += 6;
      if (bits >= 8) {
        bits -= 8;
        bytes.push((buffer >> bits) & 0xFF);
      }
    }
    return bytes;
  }

  // 字节数组 -> base64（纯 JS）
  function bytesToBase64(bytes) {
    var out = '';
    var i;
    for (i = 0; i + 2 < bytes.length; i += 3) {
      out += B64_CHARS[(bytes[i] >> 2) & 63];
      out += B64_CHARS[((bytes[i] & 3) << 4) | (bytes[i + 1] >> 4)];
      out += B64_CHARS[((bytes[i + 1] & 15) << 2) | (bytes[i + 2] >> 6)];
      out += B64_CHARS[bytes[i + 2] & 63];
    }
    if (i + 1 === bytes.length) {
      out += B64_CHARS[(bytes[i] >> 2) & 63];
      out += B64_CHARS[(bytes[i] & 3) << 4];
      out += '==';
    } else if (i + 2 === bytes.length) {
      out += B64_CHARS[(bytes[i] >> 2) & 63];
      out += B64_CHARS[((bytes[i] & 3) << 4) | (bytes[i + 1] >> 4)];
      out += B64_CHARS[(bytes[i + 1] & 15) << 2];
      out += '=';
    }
    return out;
  }

  // ===== 通用 Web API：Base64 與 UTF-8 編碼 =====
  if (typeof globalThis.atob !== 'function') {
    globalThis.atob = function (input) {
      var bytes = base64ToBytes(String(input).replace(/[\\t\\n\\f\\r ]/g, ''));
      return bytes.map(function (value) { return String.fromCharCode(value); }).join('');
    };
  }
  if (typeof globalThis.btoa !== 'function') {
    globalThis.btoa = function (input) {
      var value = String(input);
      var bytes = [];
      for (var i = 0; i < value.length; i++) {
        var code = value.charCodeAt(i);
        if (code > 255) throw new Error('InvalidCharacterError');
        bytes.push(code);
      }
      return bytesToBase64(bytes);
    };
  }

  if (typeof globalThis.TextEncoder !== 'function') {
    globalThis.TextEncoder = function () {};
    globalThis.TextEncoder.prototype.encoding = 'utf-8';
    globalThis.TextEncoder.prototype.encode = function (input) {
      return new Uint8Array(stringToBytes(String(input == null ? '' : input)));
    };
  }

  if (typeof globalThis.TextDecoder !== 'function') {
    globalThis.TextDecoder = function (label, options) {
      var encoding = String(label || 'utf-8').toLowerCase();
      if (encoding !== 'utf-8' && encoding !== 'utf8') throw new Error('Only UTF-8 decoding is supported');
      this.encoding = 'utf-8';
      this.fatal = !!(options && options.fatal);
      this.ignoreBOM = !!(options && options.ignoreBOM);
    };
    globalThis.TextDecoder.prototype.decode = function (input) {
      var bytes = input == null ? [] : Array.prototype.slice.call(input);
      var out = '';
      for (var i = 0; i < bytes.length;) {
        var a = bytes[i++] & 255;
        if (a < 128) { out += String.fromCharCode(a); continue; }
        var code = 0, needed = 0, min = 0;
        if ((a & 224) === 192) { code = a & 31; needed = 1; min = 128; }
        else if ((a & 240) === 224) { code = a & 15; needed = 2; min = 2048; }
        else if ((a & 248) === 240) { code = a & 7; needed = 3; min = 65536; }
        else { if (this.fatal) throw new Error('EncodingError'); out += '\\uFFFD'; continue; }
        var valid = true;
        for (var j = 0; j < needed; j++) {
          if (i >= bytes.length || ((bytes[i] & 192) !== 128)) { valid = false; break; }
          code = (code << 6) | (bytes[i++] & 63);
        }
        if (!valid || code < min || code > 1114111 || (code >= 55296 && code <= 57343)) {
          if (this.fatal) throw new Error('EncodingError');
          out += '\\uFFFD';
          continue;
        }
        if (code <= 65535) out += String.fromCharCode(code);
        else {
          code -= 65536;
          out += String.fromCharCode(55296 + (code >> 10), 56320 + (code & 1023));
        }
      }
      if (!this.ignoreBOM && out.charCodeAt(0) === 65279) out = out.slice(1);
      return out;
    };
  }

  // Buffer/字符串 -> base64（crypto 入参统一走这里，与洛雪 dataToB64 一致）
  function dataToB64(data) {
    if (typeof data === 'string') return bytesToBase64(stringToBytes(data));
    if (Array.isArray(data) || (data && data.length != null)) return bytesToBase64(Array.prototype.slice.call(data));
    throw new Error('data type error: ' + typeof data);
  }

  var lxUtils = {
    // buffer 完整实现（洛雪移动版语义）：六音源在自举阶段会直接调用 utils.buffer.from，
    // v243 曾改为「存在但调用即抛错」导致六音源启用失败，已回退为完整实现
    buffer: {
      from: function (input, encoding) {
        if (typeof input === 'string') {
          switch (encoding) {
            case 'binary':
              throw new Error('Binary encoding is not supported for input strings');
            case 'base64':
              return new Uint8Array(base64ToBytes(input));
            case 'hex':
              return new Uint8Array(input.match(/.{1,2}/g).map(function (byte) { return parseInt(byte, 16); }));
            default:
              return new Uint8Array(stringToBytes(input));
          }
        } else if (Array.isArray(input)) {
          return new Uint8Array(input);
        } else {
          throw new Error('Unsupported input type: ' + input + ' encoding: ' + encoding);
        }
      },
      bufToString: function (buf, format) {
        if (Array.isArray(buf) || (buf && buf.length != null)) {
          var arr = Array.prototype.slice.call(buf);
          switch (format) {
            case 'binary':
              return buf;
            case 'hex':
              return arr.reduce(function (str, byte) { return str + (byte < 16 ? '0' : '') + byte.toString(16); }, '');
            case 'base64':
              return bytesToBase64(arr);
            case 'utf8':
            case 'utf-8':
            default:
              return bytesToString(arr);
          }
        } else {
          throw new Error('Input is not a valid buffer: ' + buf + ' format: ' + format);
        }
      }
    },
    crypto: {
      aesEncrypt: function (buffer, mode, key, iv) {
        switch (mode) {
          case 'aes-128-cbc':
            return new Uint8Array(base64ToBytes(nativeCall('aes_encrypt', {
              data: dataToB64(buffer),
              key: dataToB64(key),
              iv: dataToB64(iv),
              mode: 'cbc'
            })));
          case 'aes-128-ecb':
            return new Uint8Array(base64ToBytes(nativeCall('aes_encrypt', {
              data: dataToB64(buffer),
              key: dataToB64(key),
              iv: '',
              mode: 'ecb'
            })));
          default:
            throw new Error('Binary encoding is not supported for input strings');
        }
      },
      md5: function (str) {
        if (typeof str !== 'string') throw new Error('param required a string');
        // 与洛雪移动版一致：先 encodeURIComponent 再求 MD5
        return nativeCall('md5', { str: encodeURIComponent(str) });
      },
      randomBytes: function (size) {
        var byteArray = new Uint8Array(size);
        for (var i = 0; i < size; i++) {
          byteArray[i] = Math.floor(Math.random() * 256);
        }
        return byteArray;
      }
    }
  };

  // ===== globalThis.lx =====
  globalThis.lx = {
    version: '2.0.0',
    env: 'mobile',
    EVENT_NAMES: EVENT_NAMES,
    request: lxRequest,
    on: lxOn,
    send: lxSend,
    utils: lxUtils,
    currentScriptInfo: {}
  };

  // ===== Java -> JS：填充 currentScriptInfo（源脚本元数据，参考洛雪 lx_setup）=====
  // 部分音源（如玉宁熙）会校验 currentScriptInfo.version/name，缺失则报"初始化失败"
  globalThis.__lx_setup__ = function (infoJson) {
    var info = (typeof infoJson === 'string') ? JSON.parse(infoJson) : (infoJson || {});
    globalThis.lx.currentScriptInfo = {
      id: info.id || '',
      name: info.name || '',
      description: info.description || '',
      version: info.version || '',
      author: info.author || '',
      homepage: info.homepage || '',
      rawScript: info.rawScript || ''
    };
    return null;
  };

  // ===== Java -> JS：派发 request 事件（dispatchEvent 使用）=====
  // 调用 events.request(data)，返回 holder{done,value,error}，Java 侧轮询 holder.done
  globalThis.__lx_dispatch__ = function (action, dataJson) {
    var holder = { done: false, value: null, error: null };
    var handler = events.request;
    if (typeof handler !== 'function') {
      holder.done = true;
      holder.error = 'request handler not registered';
      return holder;
    }
    var data = (typeof dataJson === 'string') ? JSON.parse(dataJson) : dataJson;
    var completed = false;
    function finish(value, error) {
      if (completed) return;
      completed = true;
      holder.done = true;
      holder.value = value;
      // 字串維持原值（播放 URL／歌詞相容）；物件與陣列轉成 JSON，供瀏覽資料層解析。
      var serialized;
      try {
        serialized = (typeof value === 'string') ? value : JSON.stringify(value);
      } catch (e) {
        serialized = String(value);
      }
      holder.valueString = (serialized === undefined) ? String(value) : serialized;
      holder.error = error;
    }
    try {
      var p = handler(data);
      // handler 必须返回 Promise，统一用 Promise.resolve 包装
      Promise.resolve(p).then(
        function (v) { finish(v, null); },
        function (e) { finish(null, String((e && e.message) || e)); }
      );
    } catch (e) {
      finish(null, String((e && e.message) || e));
    }
    return holder;
  };

  // ===== Java -> JS：响应注入（HTTP 完成 / 定时器到期）=====
  globalThis.__lx_on_response__ = function (type, dataJson) {
    var d = (typeof dataJson === 'string') ? JSON.parse(dataJson) : dataJson;
    if (type === 'http') {
      var cb = requestQueue[d.key];
      if (typeof cb === 'function') {
        delete requestQueue[d.key];
        if (d.error) {
          cb(d.error, null, null);
        } else {
          // 洛雪桌面版 needle 语义：body 尝试 JSON.parse（成功为对象，失败保持原始字符串）。
          // 六音等源在回调里直接访问 resp.body.xxx，body 为字符串时会取到 undefined 导致校验失败
          var body = d.body;
          try { body = JSON.parse(body); } catch (e) {}
          var resp = {
            statusCode: d.statusCode,
            statusMessage: d.statusMessage || '',
            headers: d.headers || {},
            body: body
          };
          cb(null, resp, body);
        }
      }
    } else if (type === 'timer') {
      var tcb = timerCallbacks[d.id];
      if (typeof tcb === 'function') {
        delete timerCallbacks[d.id];
        tcb();
      }
    }
    return null;
  };

  // ===== Java -> JS：查询 request 处理器是否已注册 =====
  globalThis.__lx_has_handler__ = function (eventName) {
    return typeof events[eventName] === 'function';
  };
})();
    """.trimIndent()
}
