package com.example.servicio1.configs.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.preauth.PreAuthenticatedAuthenticationToken;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

public class ApiKeyAuthenticationFilter extends OncePerRequestFilter {
    // 1. Ya no guardamos el secreto aquí.
    //    En su lugar, guardamos el que nos pasan.
    private final String requiredApiKey;

    // 2. Creamos un constructor para la Inyección de Dependencias
    public ApiKeyAuthenticationFilter(String requiredApiKey) {
        this.requiredApiKey = requiredApiKey;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {

        String apiKey = request.getHeader("X-API-Key");

        // 3. Comparamos contra la clave inyectada
        if (apiKey != null && apiKey.equals(this.requiredApiKey)) {
            // El resto de tu lógica es perfecta...
            PreAuthenticatedAuthenticationToken authentication =
                new PreAuthenticatedAuthenticationToken(
                        "servicio-ia", // Principal
                        null,          // Credenciales
                        Collections.singletonList(new SimpleGrantedAuthority("ROLE_SERVICE"))
                );

            SecurityContextHolder.getContext().setAuthentication(authentication);

            filterChain.doFilter(request, response);
            return; // Importante: Salimos para no ejecutar el JwtFilter
        }

        // Si no hay API Key, dejamos que el JwtFilter haga su trabajo
        filterChain.doFilter(request, response);
    }
}
