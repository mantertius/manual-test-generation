# Geração de Testes Manuais usando LLMs
Este projeto foca na criação de testes manuais utilizando Modelos de Linguagem Natural (LLMs). O objetivo é desenvolver uma suíte de casos de teste manuais que possam ser utilizados para validar a funcionalidade de uma aplicação ou sistema.

# Prompt
Para padronizar, estamos usando este prompt:

```md
You are a specialist in natural language tests and you need to create a manual test case suite with 4 test cases for the provided screenshot. Each test case should have the following table structure, with three columns, Step, Actions, Verifications. Also, add a title to each table.

Please show the results for the screenshot in the specified format, without comments.
```

## Como Contribuir

1. Faça um fork do projeto.
2. Crie uma nova branch (`git checkout -b feature/nome-da-sua-feature`).
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`).
4. Faça push para a branch (`git push origin feature/nome-da-sua-feature`).
5. Abra um Pull Request.
