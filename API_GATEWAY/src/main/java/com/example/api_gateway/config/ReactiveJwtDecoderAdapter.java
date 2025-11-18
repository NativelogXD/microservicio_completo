package com.example.api_gateway.config;

import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.ReactiveJwtDecoder;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

/**
 * Nuestro propio adaptador personalizado para convertir un JwtDecoder
 * (sincrónico/bloqueante) en un ReactiveJwtDecoder (asincrónico/no-bloqueante).
 * * Hacemos esto para evitar los problemas de importación con
 * DelegatingReactiveJwtDecoder.
 */
public class ReactiveJwtDecoderAdapter implements ReactiveJwtDecoder {

    private final JwtDecoder decoder;

    public ReactiveJwtDecoderAdapter(JwtDecoder decoder) {
        this.decoder = decoder;
    }

    @Override
    public Mono<Jwt> decode(String token) {
        // Ejecuta la decodificación (que es bloqueante) en un hilo separado
        // para no bloquear el hilo principal del Gateway (Netty).
        return Mono.fromCallable(() -> this.decoder.decode(token))
                .subscribeOn(Schedulers.boundedElastic());
    }
}
