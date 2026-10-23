# Diretrizes Globais de Retenção de Conhecimento (ARCH.md)

**ATENÇÃO AGENTES:** Sob nenhuma hipótese violem estas regras.

1. **Estrutura Obrigatória:** Todo novo projeto DEVE ter uma pasta chamada docs. Dentro dessa pasta docs, deve existir um arquivo .md chamado ARCH.md. Se for um projeto antigo reaberto e não tiver esse arquivo, crie a pasta e o arquivo imediatamente.
2. **Edição Incremental:** O arquivo ARCH.md deve ser ESTRITAMENTE INCREMENTAL. Você está **PROIBIDO** de realizar overwrite (sobrescrever ou apagar conteúdo existente) neste arquivo em qualquer hipótese.
3. **Catálogo de Problemas:** Todos os problemas (Gotchas) devem ser catalogados em tópicos. As soluções aplicadas devem ser catalogadas como subtópicos e explicitamente marcadas com o status da ação (ex: 🟢 Sucesso, 🔴 Falha, etc).
4. **Proteção Contra Sobrescrita:** Em hipótese alguma deve ser feito o overwrite do arquivo, pois ele é o melhor instrutor que teremos para não repetir os erros do passado da equipe. Só use o modo *Append* ou multi-replace com extremo cuidado.
5. **Proteção Contra Exclusão:** Não delete o arquivo ARCH.md a menos que o usuário solicite explicitamente.
6. **Reiteração de Segurança:** Repetindo: o ARCH.md é estritamente incremental. Não faça overwrite nele! Leia o arquivo antes de qualquer ação arquitetural.
