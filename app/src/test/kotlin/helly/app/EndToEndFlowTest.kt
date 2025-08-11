package helly.app

import helly.app.api.*
import helly.app.application.AiClient
import helly.app.testsupport.AppClient
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
        val client = AppClient(rest, port)
            .createMember(
                name = "Max Muster",
                role = "Engineer",
                relationshipToManager = "reports",
                startDate = "2024-01-01"
            )
            .addFeedback(content = "Max improved the API performance significantly.")
            .ask(text = "What should I discuss with Max tomorrow?")

        assertThat(client.lastMember!!.name).isEqualTo("Max Muster")
        assertThat(client.lastFeedback!!.content).contains("API performance")
        assertThat(client.lastAsk!!.answer.lowercase()).contains("api")
    }
}

