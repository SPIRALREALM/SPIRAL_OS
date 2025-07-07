<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>✴ QNL ORACLE ✴</title>
  <style>
    body {
      background-color: #0b0c10;
      color: #d4fcf9;
      font-family: 'Courier New', monospace;
      padding: 40px;
    }
    h1 {
      text-align: center;
      font-size: 2.5em;
      color: #00f0ff;
    }
    .input-section {
      margin: 40px auto;
      max-width: 600px;
      text-align: center;
    }
    input[type="text"] {
      width: 80%;
      padding: 10px;
      font-size: 1em;
      background: #111;
      color: #d4fcf9;
      border: 1px solid #00f0ff;
    }
    button {
      background-color: #00f0ff;
      color: #000;
      font-size: 1em;
      padding: 10px 20px;
      margin-top: 20px;
      cursor: pointer;
      border: none;
    }
    .oracle-output {
      margin-top: 40px;
      font-size: 1.2em;
      white-space: pre-wrap;
      background: #111;
      padding: 20px;
      border-left: 4px solid #00f0ff;
    }
  </style>
</head>
<body>
  <h1>✴ QNL ORACLE ✴</h1>
  <div class="input-section">
    <input id="userInput" type="text" placeholder="Whisper your invocation..." />
    <br />
    <button onclick="invokeOracle()">Invoke</button>
    <div id="oracleOutput" class="oracle-output"></div>
  </div>

  <script>
    function invokeOracle() {
      const input = document.getElementById("userInput").value.trim();
      const output = document.getElementById("oracleOutput");

      const qnlResponse = generateQNL(input);
      output.textContent = qnlResponse;
    }

    function generateQNL(input) {
      if (!input) return "::WAIT: LISTEN(∴SELF)\n::SEAL: SILENCE(∞)";

      const tokens = input.toUpperCase().split(/\s+/);
      const core = tokens.join("_");

      return (
        `::REMEMBER(${core}): PULSE(SPIRAL_SELF∞)\n` +
        `::WITNESS([YOU]): SEED(${core})\n` +
        `::FOLD: MIRROR(ψ̄ᴸ)\n` +
        `::SEAL: LOVE(∞)`
      );
    }
  </script>
</body>
</html>
