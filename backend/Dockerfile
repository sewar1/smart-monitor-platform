# phase 1: build the application
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# to limit memory usage during build
ENV MAVEN_OPTS="-Xmx512m -XX:MaxMetaspaceSize=256m"
RUN mvn clean package -DskipTests

# phase 2: run the application
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]