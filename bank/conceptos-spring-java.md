# Banco de conceptos: Spring, resiliencia y Java

Licencia: CC BY 4.0 (ver LICENSE-CONTENT.md). Cada punto trae una **respuesta de 60 segundos en inglés** para decir en voz alta y una **nota en español** con la corrección o el matiz.

Estado de verificación: redactado con ayuda de una IA (Claude) de memoria, **sin ejecutar**. Antes de citar un detalle de versión en una entrevista, contrástalo con la documentación oficial de Spring y Resilience4j.

---

## 1. `@Qualifier`, `@Primary` y beans del mismo tipo
**Answer:** "When two beans share a type, injecting by type is ambiguous and Spring throws `NoUniqueBeanDefinitionException`. `@Primary` marks the default candidate, while `@Qualifier("name")` at the injection point picks one explicitly. I use `@Qualifier` when callers need different implementations, and `@Primary` for a sensible default."

**Nota:** error frecuente: mencionar solo "qualifiers" sin explicar la diferencia con `@Primary`. Conoce ambos: `@Primary` es del lado del bean, `@Qualifier` del lado de quien inyecta.

## 2. `@ControllerAdvice` y manejo global de errores
**Answer:** "`@ControllerAdvice` (or `@RestControllerAdvice`) centralizes exception handling. Methods annotated with `@ExceptionHandler` map exceptions to HTTP responses, so controllers stay clean and every endpoint returns the same error shape. In Spring 6 I return `ProblemDetail`, the standard problem-details format."

**Nota:** error frecuente: escribir `@ControllerAdvise`; el nombre correcto es **Advice**. Un error de nombre en una prueba escrita no compila.

## 3. `@Bean` frente a `@Component`
**Answer:** "`@Component` and its stereotypes (`@Service`, `@Repository`) are for my own classes, found by component scanning. `@Bean` goes on a method inside a `@Configuration` class, and I use it for objects I can't annotate, like third-party classes, or when construction needs custom logic."

**Nota:** error frecuente: poner `@Bean` encima de una clase. **`@Bean` solo va sobre métodos**, nunca sobre una clase.

## 4. Excepción personalizada que envuelve otra
**Answer:** "I extend `RuntimeException` for unchecked business errors and always keep the cause by calling `super(message, cause)`, so the original stack trace is not lost. Checked exceptions only when the caller can realistically recover."

```java
public class UserLookupException extends RuntimeException {
    public UserLookupException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

**Nota:** error frecuente: declarar un campo `Exception e` propio y asignarlo a mano. En Java no se guarda la causa en un campo propio: se pasa al constructor padre.

## 5. Circuit Breaker
**Answer:** "A circuit breaker stops calling a failing dependency so failures don't cascade. It has three states: closed (normal), open (calls fail fast), and half-open (a few trial calls to test recovery). With Resilience4j I configure the failure-rate threshold, the wait duration in open state, and a fallback method."

## 6. Rate Limiting
**Answer:** "Rate limiting caps how many requests a client can make in a time window. Common algorithms are fixed window, sliding window and token bucket. At the API gateway I use Spring Cloud Gateway with a Redis-backed limiter, and when the limit is hit I return HTTP 429 with a `Retry-After` header."

## 7. Cache y TTL
**Answer:** "In Spring I use `@Cacheable` to store results, `@CachePut` to refresh them and `@CacheEvict` to invalidate. The TTL is not part of the abstraction: I configure it in the provider, for example Caffeine's `expireAfterWrite` or Redis's `entryTtl`. The hard part is invalidation and avoiding a cache stampede on hot keys."

## 8. Configuración H2 de Spring Boot
```properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.h2.console.enabled=true
server.port=8080
```
**Answer:** "This is an in-memory H2 database named `testdb`: data disappears when the app stops. `ddl-auto=create-drop` builds the schema from the entities at startup and drops it at shutdown. `show-sql` logs the generated SQL, the H2 console is a web UI for inspecting data, and the server runs on port 8080. It's for local development and tests, never production."

**Nota:** es habitual que pidan explicar archivos de configuración: aprende a explicarlos línea por línea. Valores comunes de `ddl-auto`: `none`, `validate`, `update`, `create`, `create-drop`.

## 9. Índice en una consulta (`WHERE property1 = 1`)
**Answer:** "Without an index the database does a full table scan, O(n). A B-tree index on `property1` turns the lookup into O(log n). The trade-off is slower writes and extra storage, so I index columns used in filters and joins, check the plan with `EXPLAIN`, and avoid `SELECT *` when a covering index could answer the query."

**Nota:** en JPA: `@Table(indexes = @Index(columnList = "property1"))`. En índices compuestos importa el orden de las columnas (prefijo izquierdo).

## 10. `volatile`
**Answer:** "`volatile` guarantees visibility: a write by one thread is immediately visible to the others, and it prevents certain reorderings. It does not make compound operations atomic, so `count++` on a volatile is still a race. For counters I use `AtomicInteger` or `synchronized`. Typical use: a stop flag, or the double-checked locking singleton."

## 11. `protected`
**Answer:** "A `protected` member is accessible within the same package and from subclasses, even if the subclass is in a different package, but in that case only through inheritance."

**Nota:** error frecuente: decir solo "mismo paquete"; falta la parte de las subclases.

## 12. `final`
**Answer:** "`final` on a variable means it can't be reassigned, but the object it points to can still change, so a final list is not immutable. A final method can't be overridden and a final class can't be extended. For real immutability I use records or `List.of`."

**Nota:** ya lo tienes como pregunta q20 en "Predice la salida".

## 13. Beans en XML frente a configuración Java
**Answer:** "XML defines beans declaratively with `<bean id class>` and `<property>` or `<constructor-arg>` elements, which is the legacy style. Java configuration with `@Configuration` and `@Bean` is type-safe and refactor-friendly, and Spring Boot favors annotations and auto-configuration. I can read XML in legacy projects, like legacy Struts or WebLogic projects."
