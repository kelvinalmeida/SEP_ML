document.addEventListener("DOMContentLoaded", () => {
    let countdownInterval = null;
    let taticaAtiva = false;

    let debateSicrono_isActive = false;
    let apresentacaoSicrona_isActive = false;
    let reuso_isActive = false;
    let envio_informacao_isActive = false;
    let current_tatic_description = 'Nenhuma tática ativa no momento.';

    const session_id = window.session_id;
    const token = window.token;
    const videos_uploaded_id = window.videos_uploaded_id;
    const domain_id = window.domain_id;
    const my_username = window.my_username;
    const my_id = window.my_id;


    // Verificar se o susuatio tem notas extras, se não tiver, exibir mensagem
    let student_extra_note = document.getElementById("student-extra-note-card-created");
    if (!student_extra_note) {
        document.getElementById("student-extra-note-card").innerHTML = '<em>Sem notas extras atribuidas.</em>';
    }

    // Verificar se o usuário é estudante e se não tem respostas de exercícios, exibir mensagem
    let student_answers_card = document.getElementById("student-answers-card-created");
    console.log("student_answers_card_created: ", student_answers_card);
    if (!student_answers_card) {
        console.log("student_answers_card>>: ", document.getElementById("student-answers-card"));
        document.getElementById("student-answers-card").innerHTML = '<em>Sem respostas de exercícios enviadas nesta sessão.</em>';
    }


    console.log("Session ID: ", session_id);

    taticDescription("Sessão finalizada ou sem tática ativa no momento.");
    function taticDescription(description) {

        if (description === 'hidden' || description === undefined || description.trim() === "") {
            description = "Nenhuma descrição disponível";
        }

        const descriptionElement = document.getElementById("current_tatic_description");

        descriptionElement.innerText = description;
    }


    function qual_tatica_esta_ativa(debate_sicrono, apresentacao_sincrona, reuso, envio_informacao) {
        debateSicrono_isActive = debate_sicrono;
        apresentacaoSicrona_isActive = apresentacao_sincrona;
        reuso_isActive = reuso;
        envio_informacao_isActive = envio_informacao;
        // console.log("Tática Ativa: ", debateSicrono, apresentacaoSicrona, reuso);
    }


    function debateSicrono(id_chat) {
        fetch(`/chat_fragment/${id_chat}/${session_id}`)
            .then(response => response.text())
            .then(html => {
                const chatHere = document.createElement("div");
                chatHere.innerHTML = html;
                chatHere.id = "debate_sicrono";

                // Reexecutar scripts
                chatHere.querySelectorAll("script").forEach(oldScript => {
                    const newScript = document.createElement("script");

                    if (oldScript.src) {
                        newScript.src = oldScript.src;
                        document.body.appendChild(newScript);

                        // Espera o carregamento e só então executa a função
                        newScript.onload = () => {
                            if (typeof initializeChatComponent === "function") {
                                initializeChatComponent();
                            }
                        };
                    } else {
                        newScript.textContent = oldScript.textContent;
                        document.body.appendChild(newScript);
                    }
                });

                const chatContainer = document.getElementById("tatic_here");
                chatContainer.innerHTML = ""; // Limpa o conteúdo anterior
                chatContainer.appendChild(chatHere);
            });

        // realod_page();
    }


    function startCountdown(remainingTime, strategyTactics, tacticName) {
        clearInterval(countdownInterval);
        let timeLeft = remainingTime;

        // Resetar estado de ativação a cada nova tática
        taticaAtiva = false;

        // Opcional: resetar todos os flags
        debateSicrono_isActive = false;
        apresentacaoSicrona_isActive = false;
        reuso_isActive = false;
        envio_informacao_isActive = false;

        countdownInterval = setInterval(() => {
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                document.getElementById("tacticTimer").innerText = "Concluído";
                fetchCurrentTactic(session_id); // Pega próxima tática
            } else {
                let minutes = Math.floor(timeLeft / 60);
                let seconds = timeLeft % 60;
                let formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                document.getElementById("tacticTimer").innerText = formattedTime;

                timeLeft--;

                // const elementToRemove = document.getElementById('chat');
                // if (elementToRemove) {
                //     elementToRemove.remove(); // Remove o próprio elemento
                // }

                // Verifica se a tática atual é "Debate Sincrono"
                if (tacticName == "Debate Sincrono") {

                    // Evitar adicionar o botão várias vezes:
                    if (!document.getElementById("debate_sicrono")) {

                        // (debate_sicrono, apresentacao_sincrona, reuso, envio_informacao)
                        qual_tatica_esta_ativa(true, false, false, false);

                        removerElemento();

                        id_chat = null;
                        for (let tatic_stra in strategyTactics) {
                            // console.log(strategyTactics[tatic_stra].name);
                            if (strategyTactics[tatic_stra].name == "Debate Sincrono") {
                                id_chat = strategyTactics[tatic_stra].chat_id;
                                break;
                            }
                        }

                        if (taticaAtiva == false) {
                            console.log("Entrando no debate sincrono");
                            debateSicrono(id_chat);
                            taticaAtiva = true;
                        }
                    }
                }
                else if (tacticName == "Apresentacao Sincrona") {
                    if (!document.getElementById("apresentacao_sincrona")) {

                        // (debate_sicrono, apresentacao_sincrona, reuso, envio_informacao)
                        qual_tatica_esta_ativa(false, true, false, false);
                        removerElemento();

                        let button = document.createElement("button");
                        button.innerHTML = `
            <span style="font-size: 1.5rem; font-weight: bold;">
                🎥 Entrar na Apresentação Síncrona
            </span>
        `;
                        button.id = "apresentacao_sincrona";

                        // Adicionando múltiplas classes do Bootstrap para destaque visual
                        button.className = "btn btn-warning shadow-lg border-3 border-dark mt-4 py-4 px-5 fs-4 rounded-pill";

                        link_do_meet = null;

                        for (let tatic_stra in strategyTactics) {
                            if (strategyTactics[tatic_stra].name == "Apresentacao Sincrona") {
                                link_do_meet = strategyTactics[tatic_stra].description;
                                break;
                            }
                        }

                        button.onclick = function () {
                            window.open(link_do_meet, "_blank");
                        };

                        let tatic_here = document.getElementById("tatic_here");
                        tatic_here.appendChild(button);
                    }
                }

                else if (tacticName == "Reuso") {
                    if (!document.getElementById("reuso_tabs")) {

                        qual_tatica_esta_ativa(false, false, true, false);
                        removerElemento();

                        const tatic_here = document.getElementById("tatic_here");

                        // Criar container das abas
                        const tabContainer = document.createElement("div");
                        tabContainer.id = "reuso_tabs";

                        tabContainer.innerHTML = `
            <ul class="nav nav-tabs" id="reusoTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="pdf-tab" data-bs-toggle="tab" data-bs-target="#pdfs" type="button" role="tab">PDFs</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="ex-tab" data-bs-toggle="tab" data-bs-target="#exercicios" type="button" role="tab">Exercícios</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="vid-tab" data-bs-toggle="tab" data-bs-target="#videos" type="button" role="tab">Vídeos</button>
                </li>
            </ul>
            <div class="tab-content mt-3">
                <div class="tab-pane fade show active" id="pdfs" role="tabpanel">
                    <div id="pdf_container"></div>
                </div>
                <div class="tab-pane fade" id="exercicios" role="tabpanel">
                    <div id="exercise_container" class="p-2">Carregando exercícios...</div>
                </div>
                <div class="tab-pane fade" id="videos" role="tabpanel">
                    <div id="video_container" class="p-2">Carregando vídeos...</div>
                </div>
            </div>
        `;


                        // Forçar o funcionamento das abas Bootstrap depois de adicionar dinamicamente
                        const tabTriggerList = tabContainer.querySelectorAll('button[data-bs-toggle="tab"]');
                        tabTriggerList.forEach(function (tabEl) {
                            tabEl.addEventListener('click', function (event) {
                                const tab = new bootstrap.Tab(tabEl);
                                tab.show();
                            });
                        });


                        tatic_here.appendChild(tabContainer);

                        // ---------- Carregar PDFs ----------
                        const pdfData = document.getElementById("pdf_data").getAttribute("data-pdfs");
                        const pdfs = JSON.parse(pdfData);

                        const pdfContainer = document.getElementById("pdf_container");

                        pdfs.forEach(pdf => {
                            fetch(`/pdfs/${pdf.id}`, {
                                headers: {
                                    "Authorization": `Bearer ${token}`
                                }
                            })
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error("Erro ao baixar PDF");
                                    }
                                    return response.blob();
                                })
                                .then(blob => {
                                    const url = URL.createObjectURL(blob);
                                    const embed = document.createElement("embed");
                                    embed.src = url;
                                    embed.type = "application/pdf";
                                    embed.width = "100%";
                                    embed.height = "600px";
                                    embed.className = "mb-3";

                                    pdfContainer.appendChild(embed);
                                })
                                .catch(error => {
                                    console.error("Erro ao carregar PDF: ", error);
                                });
                        });

                        // ----------Carregar Exercícios----------
                        fetch(`/domains/${domain_id}/exercises`, {
                            headers: {
                                "Authorization": `Bearer ${token}`
                            }
                        })
                            .then(res => res.json())
                            .then(data => {
                                const container = document.getElementById("exercise_container");

                                if (data.length === 0) {
                                    container.innerHTML = "<p class='text-muted'>Nenhum exercício encontrado.</p>";
                                    return;
                                }

                                // Cria o formulário principal
                                const form = document.createElement("form");
                                form.id = "exerciseForm";

                                console.log("Exercícios carregados:", data);

                                // Para cada exercício, cria um bloco com as perguntas
                                data.forEach((ex, index) => {
                                    const div = document.createElement("div");
                                    div.className = "mb-3 border rounded p-2 bg-light";
                                    div.innerHTML = `
                <p><strong>${index + 1}) ${ex.question}</strong></p>
                ${ex.options.map((opt, i) => `
                    <div>
                        <input type="radio" name="exercise_${ex.id}" value="${i}" required>
                        ${i + 1}) ${opt}
                    </div>
                `).join("")}
            `;
                                    form.appendChild(div);
                                });

                                // Botão de envio e feedback
                                form.innerHTML += `
            <button type="submit" class="btn btn-primary mt-3">Enviar respostas</button>
            <div id="formFeedback" class="mt-2 text-danger"></div>
        `;

                                container.innerHTML = ""; // Limpa qualquer conteúdo anterior
                                container.appendChild(form); // Insere o formulário

                                // Adiciona o event listener de envio DEPOIS de inserir no DOM
                                form.addEventListener("submit", function (e) {
                                    e.preventDefault();

                                    const studentName = my_username;
                                    const studentId = my_id;

                                    if (!studentName || !studentId) {
                                        document.getElementById("formFeedback").textContent = "Preencha nome e ID do aluno.";
                                        return;
                                    }

                                    const formData = new FormData(e.target);
                                    const answers = [];

                                    for (const [key, value] of formData.entries()) {
                                        if (key.startsWith("exercise_")) {
                                            const exerciseId = key.split("_")[1];
                                            answers.push({
                                                exercise_id: parseInt(exerciseId),
                                                answer: parseInt(value)
                                            });
                                        }
                                    }

                                    const totalQuestions = data.length; // Cada objeto em `data` é uma pergunta
                                    if (answers.length !== totalQuestions) {
                                        document.getElementById("formFeedback").textContent = "Responda todas as questões antes de enviar.";
                                        return;
                                    }


                                    fetch("/sessions/submit_answer", {
                                        method: "POST",
                                        headers: {
                                            "Content-Type": "application/json",
                                            "Authorization": `Bearer ${token}`
                                        },
                                        body: JSON.stringify({
                                            student_id: studentId,
                                            student_name: studentName,
                                            answers: answers,
                                            session_id: session_id,
                                        })
                                    })
                                        .then(function (response) {
                                            if (!response.ok) {
                                                throw new Error("Erro ao enviar respostas");
                                            }

                                            response.json().then(data => {
                                                document.getElementById("formFeedback").textContent = data.resp;
                                                console.log("Respostas enviadas:", data);
                                                // form.reset(); // Limpa o formulário após o envio
                                            });
                                        });
                                    // .then(response => {
                                    //     alert("Respostas enviadas com sucesso!");
                                    //     form.reset();
                                    // })
                                    // .catch(err => {
                                    //     console.error("Erro ao enviar respostas:", err);
                                    // });
                                });
                            })
                            .catch(err => {
                                console.error("Erro ao carregar exercícios:", err);
                            });


                        // ---------- Carregar Vídeos ----------
                        fetch(`/domains/${domain_id}/videos`, {
                            headers: {
                                "Authorization": `Bearer ${token}`
                            }
                        })
                            .then(res => res.json())
                            // .then(res => console.log(res))
                            .then(videos_json => {
                                const container = document.getElementById("video_container");
                                container.innerHTML = "";

                                // console.log("videos_json: ", videos_json)

                                videos_json.videos_youtube.forEach(video => {
                                    const embedUrl = convertToEmbedUrl(video.url);
                                    const div = document.createElement("div");
                                    div.className = "mb-3";
                                    div.innerHTML = `<iframe width="560" height="315" 
                                        src="${embedUrl}" 
                                        title="YouTube video player" 
                                        frameborder="0" 
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                                        allowfullscreen></iframe>`;
                                    container.appendChild(div);
                                });

                                videos_json.videos_uploaded.forEach(video => {
                                    const videoTag = document.createElement("video");
                                    const div = document.createElement("div");
                                    videoTag.controls = true;
                                    videoTag.src = `/video/uploaded/${video.id}`;
                                    videoTag.className = "w-100";
                                    div.appendChild(videoTag);
                                    container.appendChild(div);
                                });
                            })
                            .catch(err => {
                                console.error("Erro ao carregar vídeos:", err);
                            });

                    }
                }


                else if (tacticName == "Envio de Informacao") {
                    if (!document.getElementById("envio_informacao_aviso")) {

                        // (debate_sicrono, apresentacao_sincrona, reuso, envio_informacao)
                        qual_tatica_esta_ativa(false, false, false, true);
                        removerElemento();

                        // Criar container visual com mensagem e botão
                        const avisoDiv = document.createElement("div");
                        avisoDiv.id = "envio_informacao_aviso";
                        avisoDiv.className = "alert alert-info shadow-lg p-4 rounded border border-primary";

                        avisoDiv.innerHTML = `
            <h4 class="mb-3 text-primary">
                📬 Verifique seu e-mail!
            </h4>
            <p class="lead mb-4">
                Acabamos de enviar um material importante para o e-mail cadastrado.
                Por favor, confira sua caixa de entrada!
            </p>
            <button class="btn btn-success btn-lg px-4 py-2 rounded-pill fw-bold" id="btn_ver_email_gmail">
                Ir para o Gmail ✉️
            </button>
            <button class="btn btn-success btn-lg px-4 py-2 rounded-pill fw-bold" id="btn_ver_email_outlook">
                Ir para o Outlook ✉️
            </button>
        `;

                        // Adicionar ação ao botão
                        avisoDiv.querySelector("#btn_ver_email_gmail").onclick = function () {
                            window.open("https://mail.google.com/", "_blank");
                        };

                        avisoDiv.querySelector("#btn_ver_email_outlook").onclick = function () {
                            window.open("https://outlook.live.com/", "_blank");
                        };

                        let tatic_here = document.getElementById("tatic_here");
                        tatic_here.appendChild(avisoDiv);
                    }
                }

            }

        }, 1000);
    }

    function convertToEmbedUrl(url) {
        try {
            const parsedUrl = new URL(url);
            const videoId = parsedUrl.searchParams.get("v");
            if (videoId) {
                return `https://www.youtube.com/embed/${videoId}`;
            }
            return url; // fallback: se não tiver parâmetro "v"
        } catch (e) {
            console.error("URL inválida:", url);
            return url;
        }
    }


    function removerElemento() {
        let existingPdfContainer = document.getElementById("pdf_container");
        if (existingPdfContainer && !reuso_isActive) {
            existingPdfContainer.remove();
        }

        let apresentacao_sincrona = document.getElementById("apresentacao_sincrona");
        if (apresentacao_sincrona && !apresentacaoSicrona_isActive) {
            apresentacao_sincrona.remove();
        }

        let chatElement = document.getElementById("debate_sicrono");
        if (chatElement && !debateSicrono_isActive) {
            chatElement.remove();
        }

        let envio_informacao_aviso = document.getElementById("envio_informacao_aviso");
        if (envio_informacao_aviso && !envio_informacao_isActive) {
            envio_informacao_aviso.remove();
        }
    }

    function realod_page() {
        console.log("Recarregando a página...");
        location.reload();
    }

    function fetchCurrentTactic(session_id) {
        // console.log(session_status);

        fetch(`/sessions/${session_id}/current_tactic`)
            .then(response => {
                return response.json();
            })
            .then(data => {
                console.log("Dados da tática atual: ", data);
                if (data.tactic && data.session_status === 'in-progress') {
                    document.getElementById("tacticName").innerText = data.tactic.name;
                    taticDescription(data.tactic.description || "Nenhuma descrição disponível");
                    startCountdown(data.remaining_time, data.strategy_tactics, data.tactic.name);
                } else {
                    document.getElementById("tacticName").innerText = "Sessão finalizada";
                    document.getElementById("tacticTimer").innerText = "--";
                    qual_tatica_esta_ativa(false, false, false, false);
                    removerElemento();
                    taticDescription("Sessão finalizada ou sem tática ativa no momento.");
                    clearInterval(countdownInterval);
                }
            })
            .catch(error => {
                console.error("Erro ao buscar tática atual:", error.message);
                document.getElementById("tacticName").innerText = "Erro ao carregar";
                document.getElementById("tacticTimer").innerText = "--";
            });
    }


    // Inicia a sessão ao clicar
    document.getElementById("startSessionBtn").addEventListener("click", () => {
        console.log("Iniciando a sessão", session_id);
        fetch(`/sessions/start/${session_id}`)
            .then(response => {
                console.log(response);
                if (response.ok) {
                    // console.log(response)
                    fetchCurrentTactic(session_id);
                } else {
                    alert("Sessão já iniciada ou erro ao iniciar.");
                }
            });
    });


    document.getElementById("endSessionBtn").addEventListener("click", () => {
        const confirmEnd = prompt("Tem certeza que deseja encerrar a sessão? Digite 'sim' para confirmar.");

        if (confirmEnd && confirmEnd.trim().toLowerCase() === "sim") {
            console.log("Encerrando a sessão");

            fetch(`/sessions/end/${session_id}`)
                .then(response => {
                    if (response.ok) {
                        console.log("Sessão encerrada com sucesso");
                        location.reload(); // só recarrega após sucesso
                    } else {
                        alert("Erro ao encerrar a sessão.");
                    }
                })
                .catch(err => {
                    console.error("Erro na requisição:", err);
                    alert("Erro ao tentar encerrar a sessão.");
                });

        } else {
            alert("Encerramento cancelado.");
        }
    });


    // Inicia o chat automaticamente se a sessão já estiver em andamento
    function iniciarChat() {
        let session_status = '';

        fetch(`/sessions/status/${session_id}`)
            .then(response => {
                return response.json()
            }).then(data => {
                // console.log("Status da sessão: ", data);
                if (data.status === 'in-progress') {
                    // session_status = data.status;
                    fetchCurrentTactic(session_id);
                    setInterval(() => fetchCurrentTactic(session_id), 15000);
                }
            })
    }

    iniciarChat();

    // fetchCurrentTactic(session_id);
    // setInterval(() => fetchCurrentTactic(session_id), 15000);
});