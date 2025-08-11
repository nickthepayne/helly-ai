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
        @RequestParam(name = "member_ref", required = false) memberRef: String?,
        @RequestParam(name = "from", required = false) from: String?,
        @RequestParam(name = "to", required = false) to: String?
    ): List<FeedbackDTO> {
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }
}

data class FeedbackCreateDTO(
    val content: String,
    val created_at: String?,
    val person_hint: String?
)

data class FeedbackDTO(
    val id: String,
    val team_member_id: String,
    val content: String,
    val created_at: String
)

