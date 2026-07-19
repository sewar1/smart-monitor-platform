# Build Phase
# FROM eclipse-temurin:21-jdk-alpine AS build
# WORKDIR /app

# install maven to build the backend service
#RUN apk add --no-cache maven

# copy the entire project directory to the container
#COPY .mvn/ .mvn/
#COPY mvnw .
#COPY backend/pom.xml ./pom.xml
#COPY backend/src ./src

#RUN chmod +x mvnw
# run mvn clean package -DskipTests
#RUN ./mvnw clean package -DskipTests

# Run Phase
#FROM eclipse-temurin:21-jre-alpine
#WORKDIR /app
#COPY --from=build /app/backend/target/*.jar app.jar
#ENTRYPOINT ["java", "-jar", "app.jar"]

# Because I don't have Maven installed on my Windows machine, I will use the Maven Docker image to build the backend service. This way, I can build the backend service without having to install Maven on my local machine. The Maven Docker image comes with Maven pre-installed, so I can use it to build the backend service without having to worry about installing Maven on my local machine.
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app

# 2. نسخ ملفات الـ backend فقط (بما أن السياق هو الجذر، انسخ من مجلد backend)
COPY backend/pom.xml .
COPY backend/src ./src
# to enable live code updates during development in ubuntu, but not recommended for production due to performance and security concerns.
RUN mvn clean package -DskipTests

# this command will list the contents of the /app/target/ directory to verify that the JAR file has been created successfully. This is useful for debugging and ensuring that the build process has completed as expected.
RUN ls -l /app/target/

# Run Phase
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
# Copy the JAR file from the build stage to the current folder named app.jar because Spring Boot typically generates a JAR file with a versioned name, we rename it to app.jar for consistency.
# Use the filename that Spring Boot typically generates (look for the file within the target)
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]