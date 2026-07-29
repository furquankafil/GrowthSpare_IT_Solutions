# GrowthSpare IT Solutions - Platform Production Deployment Guide

This operations guide details steps to securely provision, containerize, and deploy the GrowthSpare IT Solutions platform to hosting providers (including Render, Railway, and dedicated Linux VPS nodes).

---

## 🚀 1. Automated Docker Compose VPS Provisioning (DigitalOcean, AWS, Linode)

To deploy the entire production stack (including Nginx proxying, Redis, and a hardened PostgreSQL database instance) on a raw Ubuntu VPS node:

### Prerequisite System Packages
Ensure your host node has Docker and Docker Compose installed:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable --now docker