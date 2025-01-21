# DigilogPi

Um projeto para "digitalizar" câmeras analógicas 📷

___

<div align="center">
  <img src="https://i.imgur.com/lrFmhiQ.gif" alt="YashiGIF" width="100">

  
  A ideia é aproveitar sensores como do Raspberry Pi (e o próprio) para servir de embarcado e substituto dos
  filmes, o controle de velocidade do obturador, diafragma e foco são todos dependentes da configuração
  mecânica da câmera usada, então quanto mais ela permitir, melhor!

  Começando os testes com um Raspberry Pi Zero 2 W (para ser pequeno o suficiente e não atrapalhar tanto)
  e um sensor de 5mp, mas há a possibilidade de um com maior resolução, entretanto, manter os gastos bem
  enxutos também seria uma ótima ideia...

  Um dos desafios a enfrentar é o efeito de crop que acontece pelo sensor ser menor do que a área do filme
  fotográfico, então pode ser que lentes com um campo de visão mais aberto se saiam melhor nos testes, e de
  pensar que apesar da talvez baixa qualidade poderia ser atingido um resultado (em zoom) próximo ao de uma
  telefoto com uma lente mais comum é bem animador!
  
</div>

___

  <div align="center">
  <img src="https://i.imgur.com/o5vuyb0.png" alt="ExemploDeSetup" width="300">

  Pois é, outro desafio que me esqueci (e que estou penando com ele agora 😅) é o alinhamento do sensor
  com o plano do filme da câmera, e como esse modelo que estou usando não tem opção de bulb (poder manter
  as cortinas e o diafragma abertos segurando o botão de disparo) nem de nenhuma outra coisa a não ser o
  disparo normal, os testes tomam bastante, mas bastante tempo mesmo...
  Esqueci de citar o tipo de setup do projeto, estou usando uns 5 botões e uma tela SPI 240x240 para dar
  a preview, ver a galeria e as alterações no iso e na velocidade do obturador, mais detalhes depois!
  Como apesar de ter deixado toda a configuração de captura no software definida ainda se tem um certo delay
  entre apertar o botão e realmente estar caturando a foto, sincronizar os obturadores ainda está bem sofrido,
  mas com persistência é possível ir encontrando uma posição melhor, volto assim que tiver mais atualizações
  do projeto 👍
  
</div>

___

# Comentários Adicionais



+ A implementação do código no Raspberry (para não depender de controle externo) depende de adicioná-lo no boot
com rc.local (ou com service), e ativar o login automático (faça testes antes de definir tudo!)

+ Em uma lente como 40mm, o efeito de crop com o sensor usado (OV5647) entrega ~273mm, se quiser fazer o cálculo, calcule a diagonal do sensor/filme esperado (nesse caso ~43,2mm) dividido pelo usado (~6,35mm) 

+ O módulo do sensor deve estar "puro", nesse caso sem lente, então tome cuidado na hora de retirar e tente manter o filtro de infra-vermelho ou coloque um na lente em que estiver usando, ao menos que realmente queira o efeito ou explorar uma câmera térmica, que acaba sendo bem legal também!

+ Não se assuste se não conseguir nenhuma imagem que faça sentido em ambientes internos, o alcance e o foco da lente provavelmente vão ser bem diferentes do esperado, tente com ambientes externos ou objetos/lugares a longa distância e sempre que possível confira se o alinhamento do sensor com o plano do filme está correto e centralizado, com persistência vai conseguir!
