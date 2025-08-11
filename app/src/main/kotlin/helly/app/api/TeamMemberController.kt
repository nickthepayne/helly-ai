package helly.app.api

import helly.app.application.TeamMemberRepository
import helly.app.domain.TeamMember
import org.springframework.web.bind.annotation.*
import java.util.UUID

@RestController
@RequestMapping("/v1/team-members")
class TeamMemberController(private val repo: TeamMemberRepository) {
    @PostMapping
    fun createTeamMember(@RequestBody body: TeamMemberCreateDTO): TeamMemberDTO {
        val member = TeamMember(
            id = UUID.randomUUID().toString(),
            name = body.name,
            role = body.role,
            relationshipToManager = body.relationshipToManager,
            startDate = body.startDate
        )
        val saved = repo.create(member)
        return TeamMemberDTO(
            id = saved.id,
            name = saved.name,
            role = saved.role,
            relationshipToManager = saved.relationshipToManager,
            startDate = saved.startDate
        )
    }

    @GetMapping("/{id}")
    fun getTeamMember(@PathVariable id: String): TeamMemberDTO {
        val m = repo.get(id) ?: throw IllegalArgumentException("not found")
        return TeamMemberDTO(m.id, m.name, m.role, m.relationshipToManager, m.startDate)
    }

    @GetMapping
    fun listTeamMembers(@RequestParam(required = false) search: String?): List<TeamMemberDTO> {
        return repo.list(search).map { TeamMemberDTO(it.id, it.name, it.role, it.relationshipToManager, it.startDate) }
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

