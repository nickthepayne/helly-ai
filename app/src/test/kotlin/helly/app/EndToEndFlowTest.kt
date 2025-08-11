package helly.app

import helly.app.api.*
import helly.app.application.AiClient
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.boot.test.web.server.LocalServerPort
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Import
import org.springframework.context.annotation.Primary
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import java.util.*

@SpringBootTest(classes = [Application::class], webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Import(EndToEndFlowTest.TestOverrides::class)
class EndToEndFlowTest {

    @LocalServerPort
    private var port: Int = 0

    @Autowired
    lateinit var rest: TestRestTemplate

    @Configuration
    class TestOverrides {
        @Bean
        @Primary
        fun aiClientMock(): AiClient = object : AiClient {
            override fun ask(text: String): AskResponseDTO = AskResponseDTO(
                answer = "Based on recent feedback: discuss API performance and communication.",
                citations = listOf(FeedbackRef(id = UUID.randomUUID().toString(), createdAt = "2024-06-01T10:00:00Z", snippet = "Max improved the API performance significantly."))
            )
            override fun ingestAll(teamMemberId: String, items: List<helly.app.domain.Feedback>) { /* no-op */ }
        }
    }

    @Test
    fun `create team member, add feedback, then ask a question`() {
        // 1) Create team member
        val headers = HttpHeaders(); headers.contentType = MediaType.APPLICATION_JSON
        val createMember = mapOf(
            "name" to "Max Muster",
            "role" to "Engineer",
            "relationshipToManager" to "reports",
            "startDate" to "2024-01-01"
        )
        val memberResp = rest.postForEntity("http://localhost:$port/v1/team-members", HttpEntity(createMember, headers), TeamMemberDTO::class.java)
        assertThat(memberResp.statusCode.is2xxSuccessful).isTrue
        val memberId = memberResp.body!!.id

        // 2) Add feedback (no member id provided; test hint carries the id for now)
        val addFeedback = mapOf(
            "content" to "Max improved the API performance significantly.",
            "personHint" to memberId
        )
        val fbResp = rest.postForEntity("http://localhost:$port/v1/feedback", HttpEntity(addFeedback, headers), FeedbackDTO::class.java)
        assertThat(fbResp.statusCode.is2xxSuccessful).isTrue
        assertThat(fbResp.body!!.teamMemberId).isEqualTo(memberId)

        // 3) Ask a question (delegates to mocked AI)
        val askBody = mapOf("text" to "What should I discuss with Max tomorrow?")
        val askResp = rest.postForEntity("http://localhost:$port/v1/ask", HttpEntity(askBody, headers), AskResponseDTO::class.java)
        assertThat(askResp.statusCode.is2xxSuccessful).isTrue
        assertThat(askResp.body!!.answer.lowercase()).contains("api")
    }
}

