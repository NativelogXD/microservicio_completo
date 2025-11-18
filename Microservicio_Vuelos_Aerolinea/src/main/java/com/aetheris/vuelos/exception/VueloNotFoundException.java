package com.aetheris.vuelos.exception;

public class VueloNotFoundException extends RuntimeException {
    private final String resourceName;
    private final String fieldName;
    private final long fieldValue;
    private final String fieldValueStr;

    public VueloNotFoundException(String message) {
        super(message);
        this.resourceName = "Vuelo";
        this.fieldName = "id";
        this.fieldValue = 0L;
        this.fieldValueStr = null;
    }

    public VueloNotFoundException(String resourceName, String fieldName, long fieldValue) {
        super(String.format("%s no se ha encontrado con %s: %d", resourceName, fieldName, fieldValue));
        this.resourceName = resourceName;
        this.fieldName = fieldName;
        this.fieldValue = fieldValue;
        this.fieldValueStr = null;
    }

    public VueloNotFoundException(String resourceName, String fieldName, String fieldValueStr) {
        super(String.format("%s no se ha encontrado con %s: %s", resourceName, fieldName, fieldValueStr));
        this.resourceName = resourceName;
        this.fieldName = fieldName;
        this.fieldValueStr = fieldValueStr;
        this.fieldValue = 0L;
    }

    // Getters para que el Handler pueda acceder a la información
    public String getResourceName() {
        return resourceName;
    }

    public String getFieldName() {
        return fieldName;
    }

    public long getFieldValue() {
        return fieldValue;
    }

    public String getFieldValueStr() {
        return fieldValueStr;
    }
}
