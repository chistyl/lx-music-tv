package com.lxmusic.tv.data.source

import com.lxmusic.tv.data.model.SourceBrowseActionResult
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SourceBrowsePayloadParserTest {

    private val parser = SourceBrowsePayloadParser()

    @Test
    fun `preserves arbitrary object response without assuming field names`() {
        val result = parser.parse(
            sourceId = "source-1",
            platformKey = "custom-platform",
            action = "fetchCatalog",
            rawJson = """{"catalog":{"entries":[{"uid":"a1","title":"Track"}]},"next":"cursor-2"}"""
        )

        assertTrue(result is SourceBrowseActionResult.Success)
        val payload = (result as SourceBrowseActionResult.Success).payload
        assertEquals("source-1", payload.sourceId)
        assertEquals("custom-platform", payload.platformKey)
        assertEquals("fetchCatalog", payload.action)
        val root = payload.rawData as JsonObject
        assertTrue(root["catalog"] is JsonObject)
        assertEquals("cursor-2", root["next"]?.let { (it as JsonPrimitive).content })
    }

    @Test
    fun `preserves array response`() {
        val result = parser.parse("s1", "p1", "list", """[{"id":"1"},{"id":"2"}]""")
        assertTrue(result is SourceBrowseActionResult.Success)
        assertEquals(2, ((result as SourceBrowseActionResult.Success).payload.rawData as JsonArray).size)
    }

    @Test
    fun `preserves primitive response`() {
        val result = parser.parse("s1", "p1", "count", "42")
        assertTrue(result is SourceBrowseActionResult.Success)
        assertEquals("42", ((result as SourceBrowseActionResult.Success).payload.rawData as JsonPrimitive).content)
    }

    @Test
    fun `rejects invalid json`() {
        val result = parser.parse("s1", "p1", "list", "{invalid")
        assertTrue(result is SourceBrowseActionResult.Error)
    }

    @Test
    fun `rejects missing source metadata and empty payload`() {
        assertTrue(parser.parse("", "p1", "list", "[]") is SourceBrowseActionResult.Error)
        assertTrue(parser.parse("s1", "", "list", "[]") is SourceBrowseActionResult.Error)
        assertTrue(parser.parse("s1", "p1", "", "[]") is SourceBrowseActionResult.Error)
        assertTrue(parser.parse("s1", "p1", "list", "") is SourceBrowseActionResult.Error)
    }
}
