package helly.app.api

import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/feedback")
class FeedbackController {
    @PostMapping
    fun addFeedback(@RequestBody body: FeedbackCreateDTO): FeedbackDTO {
        // Derive team member via EntityResolutionService (design only)
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }

    @GetMapping
    fun listFeedback(
        @RequestParam(name = "memberId", required = false) memberId: String?,
        @RequestParam(name = "from", required = false) from: String?, // optional time filter (ISO8601)
        @RequestParam(name = "to", required = false) to: String? // optional time filter (ISO8601)
    ): List<FeedbackDTO> {
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
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

