package com.example.api_gateway.config; // Asegúrate que tu package sea este
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.jwt.ReactiveJwtDecoder;
import org.springframework.security.web.server.SecurityWebFilterChain;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

// --- 1. IMPORTACIONES DE CORS (NECESARIAS) ---
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;
import java.util.Arrays;

// --- 2. IMPORTACIONES PARA LEER LA COOKIE (¡LAS QUE FALTABAN!) ---
import org.springframework.http.HttpCookie;
import org.springframework.security.oauth2.server.resource.authentication.BearerTokenAuthenticationToken;
import org.springframework.security.web.server.authentication.ServerAuthenticationConverter;
import reactor.core.publisher.Mono;
import org.springframework.security.web.server.util.matcher.ServerWebExchangeMatchers;
import org.springframework.security.web.server.util.matcher.PathPatternParserServerWebExchangeMatcher;


@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {
    
    // Clave secreta para validar JWT (leída desde application.yml / entorno)
    @org.springframework.beans.factory.annotation.Value("${jwt.secret:J9arT8avL4aqP2adW7ayB1azM6aeN0afS3agJ5ahK8auY2aR4aC7aA9aZ1aaD0axV6aT5aO3aP8aqE2amL9aF7asH5aK2aN4aR8aV3aY1apB0azC6aG9aX5atJ7aaL2adM4afN8awQ0aeS3arH1auT9aP5aoE7aZ2aiV6ayB3acA8aD4ajO9aL1akF0arT7apN5abM2agS4aeW3aqY6ahJ8anU0aR9aC5aV7aX4atB1aK3aG2aL8aoD6aaF9asM0awE7anH4afP1arS5auQ2aT3aiY8aZ0ajV6a}")
    private String jwtSecret;


    // --- 3. BEAN PARA LEER LA COOKIE ---
    /**
     * Este Bean le enseña a Spring Security (Reactivo) a buscar
     * el token JWT dentro de una cookie llamada "JWT_TOKEN".
     */
    @Bean
    public ServerAuthenticationConverter cookieBearerTokenConverter() {
        return exchange -> {
            // Busca la cookie llamada "JWT_TOKEN"
            HttpCookie cookie = exchange.getRequest().getCookies().getFirst("JWT_TOKEN");
            
            if (cookie == null) {
                return Mono.empty(); // No hay cookie, no hay autenticación
            }
            
            // Si la encuentra, extrae el valor
            String token = cookie.getValue();
            
            // La presenta como si fuera un "Bearer Token" para que el
            // validador por defecto la entienda.
            return Mono.just(new BearerTokenAuthenticationToken(token));
        };
    }


    /**
     * Define la cadena de filtros de seguridad.
     */
    @Bean
    public SecurityWebFilterChain protectedChain(ServerHttpSecurity http) {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        http
            .securityMatcher(new PathPatternParserServerWebExchangeMatcher("/ServiceUsuario/api/personas/me"))
            .cors(cors -> cors.configurationSource(source))
            .csrf(ServerHttpSecurity.CsrfSpec::disable)
            .authorizeExchange(exchanges -> exchanges.anyExchange().authenticated())
            .oauth2ResourceServer(server -> server
                .bearerTokenConverter(cookieBearerTokenConverter())
                .jwt(jwt -> jwt.jwtDecoder(jwtDecoder()))
            );

        return http.build();
    }

    @Bean
    public SecurityWebFilterChain publicChain(ServerHttpSecurity http) {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        http
            .securityMatcher(ServerWebExchangeMatchers.anyExchange())
            .cors(cors -> cors.configurationSource(source))
            .csrf(ServerHttpSecurity.CsrfSpec::disable)
            .authorizeExchange(exchanges -> exchanges.anyExchange().permitAll());

        return http.build();
    }

    /**
     * Crea el Bean ReactiveJwtDecoder para validar tokens.
     */
    @Bean
    public ReactiveJwtDecoder jwtDecoder() { 
        // Evitamos la validación de longitud de io.jsonwebtoken.Keys.hmacShaKeyFor
        // porque el microservicio de Usuarios utiliza una clave (&lt;256 bits).
        SecretKey secretKey = new SecretKeySpec(jwtSecret.getBytes(java.nio.charset.StandardCharsets.UTF_8), "HmacSHA256");

        JwtDecoder nonReactiveDecoder = NimbusJwtDecoder.withSecretKey(secretKey)
            .macAlgorithm(MacAlgorithm.HS256) 
            .build();
        
        // Asumiendo que ReactiveJwtDecoderAdapter es tu clase adaptadora
        return new ReactiveJwtDecoderAdapter(nonReactiveDecoder);
    }
}
