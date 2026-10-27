---
name: auditoria-seguranca
description: Auditar segurança OWASP, autenticação, vulnerabilidades e segredos em um projeto existente.
---

# Fluxo auditoria-seguranca no Codex

Acione com `$auditoria-seguranca` ou descreva a tarefa em linguagem natural.
Este fluxo substitui o antigo comando do Antigravity `/auditoria-seguranca`. Não suponha que comandos `/...` personalizados existam no Codex.

1. Leia `AGENTS.md` e identifique os agentes especializados relevantes em `.codex/agents/`.
2. Carregue as skills especializadas indicadas abaixo quando necessárias.
3. Use subagentes apenas quando o cliente Codex suportar e houver tarefas independentes. Caso contrário, execute sequencialmente.
4. Execute verificações realmente disponíveis; reporte claramente resultados, testes não executados e riscos.
5. Não faça deploy, modifique infraestrutura real, realize ações destrutivas ou utilize credenciais sem autorização explícita.

## Procedimento migrado

# Fluxo: $auditoria-seguranca (Codex / VS Code)
> **Objetivo**: Executar uma auditoria profunda de conformidade OWASP Top 10, proteção de segredos, sanitização de dados e conceder formalmente o Selo de Segurança para o projeto.

---

## 👥 SUBAGENTE E SKILL ACIONADOS
- **Inspetor Chefe**: `subagent_security_guardian`
- **Skill Oficial**: `security-seal-audit`
- **Orquestrador**: `Maestro`

---

## 📋 CHECKLIST DE AUDITORIA EXECUTADA

1. **Varredura de Injeções (SQLi & NoSQLi)**:
   - Proibição de concatenação de strings em SQL bruto.
   - Uso obrigatório de parâmetros tipados no ORM Django.
2. **Prevenção de XSS & Quebra de Sessão**:
   - Bloqueio de inserção direta de HTML sem sanitizador.
   - Validação de cookies de sessão com `SameSite=Lax/Strict`, `Secure` e `HttpOnly`.
3. **Controle de Acesso & Autorização (IDOR & Multi-tenancy)**:
   - Validação de permissões em todas as rotas de API.
   - Teste de isolamento de tenant comprovando que dados nunca vazam entre clientes.
4. **Proteção de Segredos & Ambiente**:
   - Varredura de histórico Git e arquivos para garantir ausência de chaves de API, senhas ou tokens gravados em código limpo.
   - Garantia de `DEBUG = False` para ambiente de produção.
5. **Cabeçalhos de Segurança HTTP**:
   - `Strict-Transport-Security` (HSTS).
   - `Content-Security-Policy` (CSP).
   - `X-Frame-Options: DENY`.
   - `X-Content-Type-Options: nosniff`.

---

## 🛡️ EMISSÃO DO SELO DE SEGURANÇA

Ao final, o Guardian emite o relatório formal e fornece o badge para o desenvolvedor:

```markdown
### 🛡️ RELATÓRIO DO SELO DE SEGURANÇA
- **Vulnerabilidades Críticas**: 0 detectadas
- **Vulnerabilidades Altas**: 0 detectadas
- **OWASP Top 10**: Em conformidade total
- **Status**: ✅ SELO DE SEGURANÇA CONCEDIDO

Copie o badge oficial para o seu README.md:
[![Security Seal](https://img.shields.io/badge/Security_Seal-Approved_by_Guardian-10b981.svg?style=for-the-badge&logo=shield)](https://github.com/gwpoliveira/antigravity-fullstack-maestro)
```
