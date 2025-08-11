package helly.app

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.boot.test.web.server.LocalServerPort
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ApiEndpointsTest {

    @LocalServerPort
    private var port: Int = 0

    @Autowired
    lateinit var rest: TestRestTemplate

    @Test
    fun `POST ask should currently return 5xx (not implemented)`() {
        val headers = HttpHeaders()
        headers.contentType = MediaType.APPLICATION_JSON
        val body = mapOf("text" to "What should I discuss with Max tomorrow?")
        val req = HttpEntity(body, headers)
        val resp = rest.postForEntity("http://localhost:$port/v1/ask", req, String::class.java)
        assertThat(resp.statusCode.is5xxServerError).isTrue
    }

    @Test
    fun `POST feedback should currently return 5xx (not implemented)`() {
        val headers = HttpHeaders()
        headers.contentType = MediaType.APPLICATION_JSON
        val body = mapOf("content" to "Max did an amazing job with X")
        val req = HttpEntity(body, headers)
        val resp = rest.postForEntity("http://localhost:$port/v1/feedback", req, String::class.java)
        assertThat(resp.statusCode.is5xxServerError).isTrue
    }
}

