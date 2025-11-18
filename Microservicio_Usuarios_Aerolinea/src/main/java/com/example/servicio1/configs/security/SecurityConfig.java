package com.example.servicio1.configs.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    private final JwtAuthenticationFilter jwtFilter;
    private final ApiKeyAuthenticationFilter apiKeyFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtFilter, 
                        @Value("${app.security.internal-api-key}") String internalApiKey) {
        
        System.out.println("🔐 SecurityConfig: CONSTRUCTOR LLAMADO - Configuración de seguridad inicializándose");
        this.jwtFilter = jwtFilter;
        this.apiKeyFilter = new ApiKeyAuthenticationFilter(internalApiKey); 
        System.out.println("🔐 SecurityConfig: Filtros configurados exitosamente");
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        System.out.println("🔐 SecurityConfig: Configurando cadena de filtros de seguridad");
        
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                // ÚNICAMENTE /me requiere autenticación
                .requestMatchers(HttpMethod.GET, "/api/personas/me").authenticated()
                .requestMatchers(HttpMethod.GET, "/Servicio1/api/personas/me").authenticated()
                // TODO LO DEMÁS ES PÚBLICO
                .anyRequest().permitAll()
            )
            .sessionManagement(session -> session.disable());

        // Orden de filtros: API Key primero, luego JWT
        http.addFilterBefore(apiKeyFilter, UsernamePasswordAuthenticationFilter.class);
        http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        
        System.out.println("🔐 SecurityConfig: Cadena de filtros configurada exitosamente");
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}