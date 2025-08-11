package helly.app.domain

data class TeamMember(
    val id: String,
    val name: String,
    val role: String,
    val relationshipToManager: String,
    val startDate: String
)

data class Feedback(
    val id: String,
    val teamMemberId: String,
    val content: String,
    val createdAt: String
)

data class FeedbackCreated(
    val id: String,
    val teamMemberId: String,
    val createdAt: String
)

