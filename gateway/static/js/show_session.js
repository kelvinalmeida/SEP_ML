document.addEventListener("DOMContentLoaded", () => {
    let countdownInterval = null;
    let taticaAtiva = false;

    let debateSicrono_isActive = false;
    let apresentacaoSicrona_isActive = false;
    let reuso_isActive = false;
    let envio_informacao_isActive = false;


    const session_id = window.session_id;
    const token = window.token;

    console.log("Session ID: ", session_id);


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


                const elementToRemove = document.getElementById('chat');
                if (elementToRemove) {
                    elementToRemove.remove(); // Remove o próprio elemento
                }

                // Verifica se a tática atual é "Debate Sincrono"
                if (tacticName == "Debate Sincrono") {

                    // Evitar adicionar o botão várias vezes:
                    if (!document.getElementById("chat")) {

                        qual_tatica_esta_ativa(true, false, false);

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

                    if (!document.getElementById("pdf_container")) {

                        qual_tatica_esta_ativa(false, false, true);
                        removerElemento();

                        let pdfContainer = document.createElement("div");
                        pdfContainer.id = "pdf_container";

                        let pdfData = document.getElementById("pdf_data").getAttribute("data-pdfs");
                        let pdfs = JSON.parse(pdfData);

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
                                    let url = URL.createObjectURL(blob);
                                    let embed = document.createElement("embed");
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

                        let tatic_here = document.getElementById("tatic_here");
                        tatic_here.appendChild(pdfContainer);
                    }
                }

                else if (tacticName == "Envio de Informacao") {
                    if (!document.getElementById("chat")) {

                        qual_tatica_esta_ativa(false, false, false, true);
                        removerElemento();

                        // Criar container visual com mensagem e botão
                        const avisoDiv = document.createElement("div");
                        avisoDiv.id = "chat";
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
                    startCountdown(data.remaining_time, data.strategy_tactics, data.tactic.name);
                } else {
                    document.getElementById("tacticName").innerText = "Sessão finalizada";
                    document.getElementById("tacticTimer").innerText = "--";
                    qual_tatica_esta_ativa(false, false, false, false);
                    removerElemento();
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