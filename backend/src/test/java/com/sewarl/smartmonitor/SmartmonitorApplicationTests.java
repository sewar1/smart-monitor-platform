package com.sewarl.smartmonitor;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1",
    "spring.datasource.driver-class-name=org.h2.Driver",
    "spring.jpa.hibernate.ddl-auto=create-drop"
    // REMOVED: "spring.autoconfigure.exclude=...DataSourceAutoConfiguration"
    // This line was self-contradictory: it told Spring Boot to build an H2
    // DataSource above, but then explicitly excluded the very
    // auto-configuration class (DataSourceAutoConfiguration) responsible for
    // reading those properties and creating that DataSource bean in the
    // first place. With no DataSource bean, Spring Data JPA can't create any
    // @Repository proxies (e.g. UserRepository), which cascaded into
    // UserService and DatabaseSeeder failing to initialize, which in turn
    // failed the whole ApplicationContext for this test.
})
class SmartmonitorApplicationTests {

    @Test
    void contextLoads() {
        // Ensures the Spring context loads successfully
    }
}
