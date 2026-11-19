# docs/fusion-api-notes.md — Armadilhas da API do Fusion 360

Registrar aqui variações descobertas entre versões do Fusion, bugs e soluções.

## Armadilhas conhecidas (Seção 6.3 do ARCHITECTURE.md)

- **Unidades internas: centímetros.** `mm → cm = v / 10`. Nunca passar mm cru.
- Planos: `rootComponent.xYConstructionPlane`; deslocados via
  `constructionPlanes.createInput().setByOffset(plano, ValueInput.createByReal(cm))`.
- Círculos: `sketchCircles.addByCenterRadius(Point3D.create(x_cm, y_cm, 0), r_cm)` —
  coordenadas **no espaço do sketch**. Validar o espelhamento de Y se algum dia usar
  planos XZ/YZ.
- `extrudeFeatures.createInput(profiles, operation)`: `profiles` pode ser
  `ObjectCollection` com todos os `sketch.profiles`.
  `setDistanceExtent(False, ValueInput.createByReal(cm))`; distância negativa inverte o
  sentido; `setAllExtent(...)` para "through all".
- `cut` multi-corpo: restringir com `input.participantBodies = [corpo]`.
- Nomear: `feature.bodies.item(0).name = body_name`.
- Agrupar no *timeline* ao final
  (`design.timeline.timelineGroups.add(startIdx, endIdx)`) para o usuário desfazer o
  plano inteiro de uma vez.
- Erros em `executor` devem virar `error` no relatório; nunca deixar exceção subir para
  o handler (Fusion pode travar a UI).

## Descobertas durante implementação

_(preencher aqui se `participantBodies` não aceitar lista direta — usar `ObjectCollection` nesse caso)_
