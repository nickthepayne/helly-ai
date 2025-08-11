package helly.app.api

import helly.app.application.FeedbackRepository
import helly.app.application.FeedbackService
import helly.app.domain.Feedback
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/feedback")
class FeedbackController(private val service: FeedbackService, private val repo: FeedbackRepository) {
    @PostMapping
    fun addFeedback(@RequestBody body: FeedbackCreateDTO): FeedbackDTO {
        val saved = service.addFeedback(content = body.content, createdAt = body.createdAt, personHint = body.personHint)
        return FeedbackDTO(saved.id, saved.teamMemberId, saved.content, saved.createdAt)
    }

    @GetMapping
    fun listFeedback(
        @RequestParam(name = "memberId", required = false) memberId: String?,
        @RequestParam(name = "from", required = false) from: String?, // optional time filter (ISO8601)
        @RequestParam(name = "to", required = false) to: String? // optional time filter (ISO8601)
    ): List<FeedbackDTO> {
        return repo.list(memberId, from, to).map { FeedbackDTO(it.id, it.teamMemberId, it.content, it.createdAt) }
    }
}

data class FeedbackCreateDTO(
    val content: String,
    val createdAt: String?,
    val personHint: String?
)

data class FeedbackDTO(
    val id: String,
    val teamMemberId: String,
    val content: String,
    val createdAt: String
)

