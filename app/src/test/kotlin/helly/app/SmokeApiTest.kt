package helly.app

import org.junit.jupiter.api.Test
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.server.LocalServerPort
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.beans.factory.annotation.Autowired
import org.assertj.core.api.Assertions.assertThat

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class SmokeApiTest {

    @LocalServerPort
    private var port: Int = 0

    @Autowired
    lateinit var rest: TestRestTemplate

    @Test
    fun `should respond 404 for unknown routes (app runs)`() {
        val resp = rest.getForEntity("http://localhost:$port/v1/does-not-exist", String::class.java)
        assertThat(resp.statusCode.is4xxClientError).isTrue
    }
}

