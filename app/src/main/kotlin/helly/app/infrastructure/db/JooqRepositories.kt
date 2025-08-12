package helly.app.infrastructure.db

import helly.app.application.FeedbackRepository
import helly.app.application.TeamMemberRepository
import helly.app.domain.Feedback
import helly.app.domain.TeamMember
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile

@Profile("db")
@Configuration
class DbRepositoriesConfig {
    @Bean
    fun teamMemberRepositoryJooq(dsl: DSLContext): TeamMemberRepository = JooqTeamMemberRepository(dsl)

    @Bean
    fun feedbackRepositoryJooq(dsl: DSLContext): FeedbackRepository = JooqFeedbackRepository(dsl)
}

class JooqTeamMemberRepository(private val dsl: DSLContext) : TeamMemberRepository {
    private val TM = DSL.table("team_members")
    private val ID = DSL.field("id", String::class.java)
    private val NAME = DSL.field("name", String::class.java)
    private val ROLE = DSL.field("role", String::class.java)
    private val REL = DSL.field("relationship_to_manager", String::class.java)
    private val START = DSL.field("start_date", String::class.java)

    override fun create(member: TeamMember): TeamMember {
        dsl.insertInto(TM)
            .columns(ID, NAME, ROLE, REL, START)
            .values(member.id, member.name, member.role, member.relationshipToManager, member.startDate)
            .execute()
        return member
    }

    override fun get(id: String): TeamMember? {
        val r = dsl.select(ID, NAME, ROLE, REL, START)
            .from(TM)
            .where(ID.eq(id))
            .fetchOne() ?: return null
        return TeamMember(
            id = r.get(ID)!!,
            name = r.get(NAME)!!,
            role = r.get(ROLE)!!,
            relationshipToManager = r.get(REL)!!,
            startDate = r.get(START)!!
        )
    }

    override fun list(search: String?): List<TeamMember> {
        val cond = if (search.isNullOrBlank()) DSL.noCondition() else NAME.likeIgnoreCase("%$search%")
        return dsl.select(ID, NAME, ROLE, REL, START)
            .from(TM)
            .where(cond)
            .orderBy(NAME.asc())
            .fetch { r ->
                TeamMember(
                    id = r.get(ID)!!,
                    name = r.get(NAME)!!,
                    role = r.get(ROLE)!!,
                    relationshipToManager = r.get(REL)!!,
                    startDate = r.get(START)!!
                )
            }
    }
}

class JooqFeedbackRepository(private val dsl: DSLContext) : FeedbackRepository {
    private val FB = DSL.table("feedback")
    private val ID = DSL.field("id", String::class.java)
    private val MEMBER_ID = DSL.field("team_member_id", String::class.java)
    private val CONTENT = DSL.field("content", String::class.java)
    private val CREATED_AT = DSL.field("created_at", String::class.java)

    override fun create(feedback: Feedback): Feedback {
        dsl.insertInto(FB)
            .columns(ID, MEMBER_ID, CONTENT, CREATED_AT)
            .values(feedback.id, feedback.teamMemberId, feedback.content, feedback.createdAt)
            .execute()
        return feedback
    }

    override fun list(memberId: String?, from: String?, to: String?): List<Feedback> {
        var cond = DSL.noCondition()
        if (!memberId.isNullOrBlank()) cond = cond.and(MEMBER_ID.eq(memberId))
        if (!from.isNullOrBlank()) cond = cond.and(CREATED_AT.ge(from))
        if (!to.isNullOrBlank()) cond = cond.and(CREATED_AT.le(to))
        return dsl.select(ID, MEMBER_ID, CONTENT, CREATED_AT)
            .from(FB)
            .where(cond)
            .orderBy(CREATED_AT.asc())
            .fetch { r ->
                Feedback(
                    id = r.get(ID)!!,
                    teamMemberId = r.get(MEMBER_ID)!!,
                    content = r.get(CONTENT)!!,
                    createdAt = r.get(CREATED_AT)!!
                )
            }
    }
}

