function converterTempo(tempo) {
  tempo = tempo.replace(",", ".");
  if (tempo.includes(":")) {
    const [min, seg] = tempo.split(":").map(Number);
    return min + seg / 60;
  }
  return parseFloat(tempo);
}

function getRepertorio() {
  return JSON.parse(localStorage.getItem("repertorio") || "[]");
}

function salvarRepertorio(rep) {
  localStorage.setItem("repertorio", JSON.stringify(rep));
}

function adicionarMusica() {
  const titulo = document.getElementById("titulo").value.trim();
  const autor = document.getElementById("autor").value.trim();
  const tempo = document.getElementById("tempo").value.trim();
  const msg = document.getElementById("msg-add");

  if (!titulo || !autor || !tempo) {
    msg.innerText = "❌ Preencha todos os campos.";
    return;
  }

  try {
    const tempoMin = converterTempo(tempo);
    const rep = getRepertorio();
    rep.push({ titulo, autor, tempo_min: tempoMin, score: 0 });
    salvarRepertorio(rep);
    msg.innerText = "✅ Música adicionada!";
    document.getElementById("titulo").value = "";
    document.getElementById("autor").value = "";
    document.getElementById("tempo").value = "";
  } catch {
    msg.innerText = "❌ Tempo inválido.";
  }
}

function gerarSetlist() {
  const modo = document.querySelector("input[name='modo']:checked").value;
  const tempoAlvo = parseFloat(document.getElementById("tempo-ensaio").value);
  const rep = getRepertorio().slice().sort((a, b) => a.score - b.score);
  const list = [];
  let total = 0;

  if (modo === "fixo") {
    for (let i = 0; i < Math.min(20, rep.length); i++) {
      list.push(rep[i]);
      rep[i].score += 1;
    }
  } else {
    for (let i = 0; i < rep.length; i++) {
      const m = rep[i];
      if (total + m.tempo_min <= tempoAlvo) {
        list.push(m);
        total += m.tempo_min;
        m.score += 1;
      }
    }
  }

  salvarRepertorio(rep);
  const texto = list.map((m, i) =>
    \`\${i + 1}. \${m.titulo} - \${m.autor} (\${m.tempo_min.toFixed(2)} min)\`
  ).join("\n");
  document.getElementById("setlist").innerText = texto;
}

function mostrarRepertorio() {
  const rep = getRepertorio();
  const texto = rep.map((m, i) =>
    \`\${i + 1}. \${m.titulo} - \${m.autor} (\${m.tempo_min.toFixed(2)} min) | Score: \${m.score}\`
  ).join("\n");
  document.getElementById("repertorio").innerText = texto;
}

function baixarCSV() {
  const rep = getRepertorio();
  let csv = "titulo,autor,tempo_min,score\n";
  for (const m of rep) {
    csv += \`\${m.titulo},\${m.autor},\${m.tempo_min},\${m.score}\n\`;
  }
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "repertorio.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function importarCSV(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function (e) {
    const linhas = e.target.result.split("\n").slice(1);
    const repertorio = [];
    for (const linha of linhas) {
      const [titulo, autor, tempo_min, score] = linha.split(",");
      if (titulo && autor) {
        repertorio.push({
          titulo: titulo.trim(),
          autor: autor.trim(),
          tempo_min: parseFloat(tempo_min),
          score: parseInt(score)
        });
      }
    }
    salvarRepertorio(repertorio);
    mostrarRepertorio();
  };
  reader.readAsText(file);
}
