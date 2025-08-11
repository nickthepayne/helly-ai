package helly.app.testsupport

import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity

fun appUrl(port: Int, path: String) = "http://localhost:$port$path"

fun jsonHeaders() = HttpHeaders().apply { contentType = MediaType.APPLICATION_JSON }

inline fun <reified T> TestRestTemplate.postJson(port: Int, path: String, body: Any): ResponseEntity<T> {
    val req = HttpEntity(body, jsonHeaders())
    return this.postForEntity(appUrl(port, path), req, T::class.java)
}

inline fun <reified T> TestRestTemplate.getJson(port: Int, path: String): ResponseEntity<T> {
    val req = HttpEntity<String>(null, jsonHeaders())
    return this.getForEntity(appUrl(port, path), T::class.java)
}

