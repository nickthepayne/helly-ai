package helly.app.infrastructure.db

import org.flywaydb.core.Flyway
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.jooq.impl.DSL
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.jdbc.datasource.DriverManagerDataSource
import javax.sql.DataSource

@Configuration
class DbConfig {
    @Bean
    fun dataSource(
        @Value("\${app.db.url:jdbc:sqlite:build/helly.db}") url: String,
        @Value("\${app.db.user:}") user: String?,
        @Value("\${app.db.password:}") password: String?
    ): DataSource {
        val ds = DriverManagerDataSource()
        ds.setDriverClassName("org.sqlite.JDBC")
        ds.url = url
        if (!user.isNullOrBlank()) ds.username = user
        if (!password.isNullOrBlank()) ds.password = password
        return ds
    }

    @Bean(initMethod = "migrate")
    fun flyway(dataSource: DataSource): Flyway = Flyway.configure()
        .dataSource(dataSource)
        .locations("classpath:db/migration")
        .baselineOnMigrate(true)
        .load()

    @Bean
    fun dslContext(ds: DataSource): DSLContext = DSL.using(ds, SQLDialect.SQLITE)
}

