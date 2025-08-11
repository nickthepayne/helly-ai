package helly.app.api

import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/v1/team-members")
class TeamMemberController {
    @PostMapping
    fun createTeamMember(@RequestBody body: TeamMemberCreateDTO): TeamMemberDTO {
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }

    @GetMapping("/{id}")
    fun getTeamMember(@PathVariable id: String): TeamMemberDTO {
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }

    @GetMapping
    fun listTeamMembers(@RequestParam(required = false) search: String?): List<TeamMemberDTO> {
        throw UnsupportedOperationException("Not implemented in MVP scaffold")
    }
}

data class TeamMemberCreateDTO(
    val name: String,
    val role: String,
    val relationshipToManager: String,
    val startDate: String
)

data class TeamMemberDTO(
    val id: String,
    val name: String,
    val role: String,
    val relationshipToManager: String,
    val startDate: String
)

