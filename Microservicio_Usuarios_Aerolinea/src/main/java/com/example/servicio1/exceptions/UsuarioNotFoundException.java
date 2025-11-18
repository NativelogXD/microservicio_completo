package com.example.servicio1.exceptions;

public class UsuarioNotFoundException extends RuntimeException {
    String resourceName;// id name
    String fieldName;// id name
    long fieldValue;
    String fieldValuee;// variable
    public UsuarioNotFoundException(String resourceName, String fieldName, long fieldValue) {
        super(String.format("%s not found with %s : %d", resourceName, fieldName, fieldValue));
        this.resourceName = resourceName;
        this.fieldName = fieldName;
        this.fieldValue = fieldValue;
    }
    public UsuarioNotFoundException(String resourceName, String fieldName, String fieldValuee) {
        super(String.format("%s not found with %s : %s", resourceName, fieldName, fieldValuee)); // Usar %s para Strings
        this.resourceName = resourceName;
        this.fieldName = fieldName;
        this.fieldValuee = fieldValuee;
    }
}
