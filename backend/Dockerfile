# phase 1: build the application
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# to limit memory usage during build
ENV MAVEN_OPTS="-Xmx512m -XX:MaxMetaspaceSize=256m"
# run the maven build command to package the application, skipping tests to speed up the build process
RUN ./mvnw clean package -DskipTests

# phase 2: run the application
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
# copy the built jar file from the first phase to the second phase
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]