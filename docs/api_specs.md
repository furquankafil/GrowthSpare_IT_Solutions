# GrowthSpare IT Solutions - REST API Specification

This specification documents the public and internal REST API endpoints available on the GrowthSpare platform. These endpoints are designed for future SaaS integrations, CRM synchronization, and automated external lead capturing.

---

## 🔑 1. JWT Authentication Endpoints

These endpoints utilize standard Django REST Framework and SimpleJWT configurations to handle security tokens.

### A. Obtain Token pair
* **Route**: `POST /accounts/api/token/`
* **Access**: Public
* **Request Body**:
  ```json
  {
    "email": "partner@company.com",
    "password": "securepassword123"
  }