import os
import tkinter as tk
from datetime import datetime
import csv
from customtkinter import *
from CTkMessagebox import *
from CTkListbox import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageTk
from functools import partial
from reportlab.pdfgen import canvas
from reportlab.lib import utils
import textwrap


class CasaApoioManager:
 
    def __init__(self):
        self.data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
        self.pasta_PIA = None 

    def salvar_casa_apoio(self, dados_do_morador_pia, dados_do_morador_cadastro):
        pasta_cadastros = os.path.join(self.data_directory, "cadastros registro admissional")
        if not os.path.exists(pasta_cadastros):
            os.makedirs(pasta_cadastros)

        pasta_PIA = os.path.join(self.data_directory, "PIA")
        if not os.path.exists(pasta_PIA):
            os.makedirs(pasta_PIA)

        pia_arquivo = os.path.join(pasta_PIA, "data_pia.csv")
        dados_existentes_pia = []
        if os.path.isfile(pia_arquivo):
            with open(pia_arquivo, mode='r', newline='', encoding='utf-8') as pia_file:
                reader = csv.DictReader(pia_file)
                dados_existentes_pia = list(reader)

        nome_residente = dados_do_morador_pia["Nome do residente"]
        atualizado = False

        for i, linha in enumerate(dados_existentes_pia):
            if linha["Nome do residente"] == nome_residente:
                dados_existentes_pia[i] = dados_do_morador_pia
                atualizado = True
                break

        if not atualizado:
            dados_existentes_pia.append(dados_do_morador_pia)

        with open(pia_arquivo, mode='w', newline='', encoding='utf-8') as pia_file:
            writer = csv.DictWriter(pia_file, fieldnames=dados_do_morador_pia.keys())
            writer.writeheader()
            writer.writerows(dados_existentes_pia)


        cadastro_arquivo = os.path.join(pasta_cadastros, "data_cadastros.csv")
        file_exists = os.path.isfile(cadastro_arquivo)

        if file_exists:
            with open(cadastro_arquivo, mode='r', newline='', encoding='utf-8') as cadastro_file:
                reader = csv.DictReader(cadastro_file)
                dados_existentes = list(reader)

            rg_identificador = dados_do_morador_cadastro["RG"]
            nova_linha = True
            for i, linha in enumerate(dados_existentes):
                if linha["RG"] == rg_identificador:
                    dados_existentes[i] = dados_do_morador_cadastro
                    nova_linha = False
                    break

            if nova_linha: 
                dados_existentes.append(dados_do_morador_cadastro)

            with open(cadastro_arquivo, mode='w', newline='', encoding='utf-8') as cadastro_file:
                writer = csv.DictWriter(cadastro_file, fieldnames=dados_do_morador_cadastro.keys())
                writer.writeheader()  
                writer.writerows(dados_existentes) 
        else:
            with open(cadastro_arquivo, mode='w', newline='', encoding='utf-8') as cadastro_file:
                writer = csv.DictWriter(cadastro_file, fieldnames=dados_do_morador_cadastro.keys())
                writer.writeheader() 
                writer.writerow(dados_do_morador_cadastro)

    def carregar_moradores_admissional(self):
        janela_editar = CTk()
        janela_editar.title("Editar Morador")
        janela_editar.geometry("400x400")
        
        if os.path.exists(self.data_directory):
            pacientes_diretorios = [d for d in os.listdir(self.data_directory) if os.path.isdir(os.path.join(self.data_directory, d))]
        else:
            pacientes_diretorios = []

        self.lista_morador = CTkListbox(janela_editar, values=pacientes_diretorios)
        self.lista_morador.pack(pady=10)

        botao_editar_selecionado = CTkButton(master=janela_editar, text="Editar Selecionado", command=self.selecionar_morador)
        botao_editar_selecionado.pack(pady=20)

        janela_editar.mainloop()

    def selecionar_morador(self):

        selecionado = self.lista_morador.curselection()
        if selecionado:
            index = selecionado[0]
            self.editar_selecionado(index)

    def editar_selecionado(self):
        nome_morador = self.lista_morador.get()
        if nome_morador:
            nome_arquivo = os.path.join(self.data_directory, nome_morador, f"{nome_morador}_admissional.csv")
            if os.path.exists(nome_arquivo):
                with open(nome_arquivo, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    dados_paciente = {linha[0]: linha[1] for linha in reader if linha}

class CasaApoioApp:
    def __init__(self, root):
        self.root = root
        self.contatos = []
        self.medicamentos = []
        self.manager = CasaApoioManager()
        self.leitor = LeitorDadosCasaApoio(self.manager.data_directory, self)
        self.pdf = GeradorPDF(self.manager.data_directory, self)
        self.root.title("Apoio Fácil")
        self.root.geometry("600x400")
        set_appearance_mode("light")
        self.label_status = CTkLabel(self.root, text="")
        self.build_ui()

    def cadastro_casa_apoio(self, dados_cadastros=None):
        root.iconify()
        janela_cadastro = CTk()
        janela_cadastro.title("Cadastro")
        
        largura_tela = janela_cadastro.winfo_screenwidth()
        altura_tela = janela_cadastro.winfo_screenheight()

        largura_janela = int(largura_tela * 0.6)
        altura_janela = int(altura_tela * 0.8)

        janela_cadastro.geometry(f"{largura_janela}x{altura_janela}")
        janela_cadastro.resizable(True, True)

        self.tabview = CTkTabview(janela_cadastro)
        self.tabview.pack(expand=True, fill='both')
        self.aba1 = self.tabview.add("Dados Pessoais")
        self.aba2 = self.tabview.add("Informações Adicionais")

        scrollable_frame = CTkScrollableFrame(self.aba1)
        scrollable_frame.pack(expand=True, fill='both', padx=5, pady=5)
        scrollable_frame2 = CTkScrollableFrame(self.aba2)
        scrollable_frame2.pack(expand=True, fill='both', padx=5, pady=5)

        campos = [
            ("Nome do Residente:", "entry_nome"),
            ("Data de nascimento:", "entry_data_nascimento"),
            ("Data de entrada:", "entry_data_entrada"),
            ("RG:", "entry_RG"),
            ("CPF:", "entry_CPF"),
            ("Endereço anterior:", "entry_endereço_anterior"),
            ("Estado Civil:", "entry_estado_civil"),
            ("Nome do cônjuge:", "entry_nome_conjuge"),
            ("Número de filhos:", "entry_n_filhos"),
            ("Peso:", "entry_peso"),
            ("Altura:", "entry_altura"),
            ("Esse morador possui \nprocuração?", "cbox_procuracao"),
            ("Quem possui procuração?", "entry_procu_re"),
            ("Ou Curatela?", "cbox_cura"),
            ("Quem?", "entry_resp_cura"),
            ("Diagnóstico atual(ais):", "entry_diag"),
            ("Grau de dependência:", "cbox_depen"),
            ("Outras doenças \nassociadas:", "entry_cultura_lazer"),
            ("Alergias ou intolerâncias:", "entry_alergia"),
            ("Escolaridade:", "entry_escolaridade"),
            ("Deficiências físicas \nassociadas:", "cbox_deficiencia"),
            ("Faz uso de:", "cbox_uso"),
            ("Qual outro?", "entry_uso_outro"),
            ("Diagnósticos:", "entry_diagnostico"),
            ("Grau dependência:", "entry_depen")
        ]

        campos1 = [
            ("Motivo da opção pela moradia:", "entry_motivo_moradia"),
            ("Benefício:", "cbox_beneficio"),
            ("Qual?", "entry_qual_b"),
            ("Morador administra\nseus recursos financeiros?", "cbox_recursos"),
            ("Quem exerce isso para ele?", "entry_recursos_q"),
            ("A manutenção do morador na instituição\né paga por:", "cbox_pagamento"),
            ("Breve histórico\ndo morador(a):", "entry_historico"),
            ("Descreva como é a relação\ndo acolhido com os outros acolhidos,\ncom a equipe que trabalha na instituição\ne com a comunidade.\nSe estabeleceram vínculos de amizade\ne de namoro e se tem pessoas de referência.", "entry_rel_com"),
            ("Descrever quais talentos e\npotencialidades foram observados no acolhido\ne se está sendo desenvolvido:", "entry_poten"),
            ("Condição de autonomia:", "cbox_cond"),
            ("Como é a relação\ndos familiares com o morador(a):", "entry_re_familia"),
            ("Visão da equipe em relação\n ao relacionamento familiar:", "entry_rel_morador"),
            ("Planejamento para estreitamento\nda relação familiar:", "entry_rel_plano"),
            ("Atividades, frequência e objetivo:", "entry_rel_atividades"),
            ("Representante legal:", "cbox_representante"),
            ("Em caso de não deambulação,\nanotar forma de locomoção:", "entry_rel_ambulacao"),
            ("Recebe visitas? Quem?", "entry_rel_visita"),
            ("Já houve contato com familiares? Quem?", "entry_contatof"),
            ("Existe a possibilidade de reintegração familiar?\nJustificar:", "entry_reintegrar"),
            ("O acolhido vai visitar familiares?\nDescrever:", "entry_visita"),
            ("Recebe e faz ligações telefônicas?", "entry_telefonemas"),
            ("Aceita medicação? Qual estratégia adotada?", "entry_aceita_medica"),
            ("Aceita outros tipos de tratamento?", "entry_outros_medica"),
            ("Realiza acompanhamento externo em instituição de saúde?", "entry_acom_exter"),
            ("Transito pela instituição:", "cbox_transitar"),
            ("Alteração observada na autonomia, houve retrocesso?\nDescrever", "entry_alt_autonomia")
        ]


        opcoes_combobox = {
            "cbox_transitar": ["Livre", "Com Auxílios"],
            "cbox_depen": ["Grau de dependência I", "Grau de dependência II", "Grau de dependência III"],
            "cbox_procuracao": ["Sim", "Não"],
            "cbox_cura": ["Sim", "Não"],
            "cbox_deficiencia": ["Física", "Visual", "Auditiva", "Nenhuma"],
            "cbox_uso": ["Óculos", "Prótese", "Aparelho auditivo", "Cadeira de rodas", "Muletas", "Bengala", "Bolsa coletora", "Outras"],
            "cbox_beneficio": ["Não recebe nenhum tipo de benefício", "Benefício previdenciário - aposentadoria", "Benefício previdenciário - pensão", "Benefício assistencial - BPC", "Exerce atividade laborativa remunerada"],
            "cbox_recursos": ["Sim, sozinho.", "Não", "Sim, com auxílio."],
            "cbox_pagamento": ["Familiar", "Governo", "ONG", "Outro", "Não é pago"],
            "cbox_cond": ["Independente", "Dependente Parcial", "Totalmente Dependente"],
            "cbox_representante": ["Próprio morador", "Outro"],
        }
        

        for texto, entry_name in campos:
            frame = CTkFrame(scrollable_frame)
            frame.pack(padx=5, pady=5, fill='x')

            label = CTkLabel(frame, text=texto, width=150)
            label.pack(side='left', padx=(0, 10))

            if "cbox" in entry_name:
                opcoes = opcoes_combobox.get(entry_name, ["Sim", "Não"])
                entry = CTkComboBox(frame, values=opcoes, width=150)
                entry.bind("<<ComboboxSelected>>", lambda event, name=entry_name: self.atualizar_selecao(entry.get()))
            else:
                entry = CTkEntry(frame, width=300)

            entry.pack(side='left', fill='x')
            setattr(self, entry_name, entry)


        self.button_fechar1 = CTkButton(scrollable_frame, text="Fechar", command=lambda: (root.deiconify(), janela_cadastro.withdraw()))
        self.button_fechar1.pack(pady=20)


        for texto, entry_name in campos1:
            frame = CTkFrame(scrollable_frame2)
            frame.pack(padx=5, pady=5, fill='x')

            label = CTkLabel(frame, text=texto, width=200, anchor='w', justify='left')
            label.pack(side='left', padx=(0, 10))

            if "cbox" in entry_name:
                opcoes = opcoes_combobox.get(entry_name, ["Sim", "Não"])
                entry = CTkComboBox(frame, values=opcoes, width=150)
                entry.bind("<<ComboboxSelected>>", lambda event, name=entry_name: self.atualizar_selecao(entry.get()))
            else:
                entry = CTkEntry(frame, width=300)

            if entry_name == "entry_peso":
                entry.bind("<KeyRelease>", lambda event: self.calcular_imc())
            elif entry_name == "entry_altura":
                entry.bind("<KeyRelease>", lambda event: self.calcular_imc())          

            entry.pack(side='left', fill='x')
            setattr(self, entry_name, entry)
        self.label_imc = CTkLabel(scrollable_frame, text="")
        self.label_imc.pack(pady=(5, 0))

        mapeamento = {
            "Nome do residente": "entry_nome",
            "Data de nascimento": "entry_data_nascimento",
            "Data de entrada": "entry_data_entrada",
            "RG": "entry_RG",
            "CPF": "entry_CPF",
            "Endereço Anterior": "entry_endereço_anterior",
            "Estado Civil": "entry_estado_civil",
            "Nome do cônjuge": "entry_nome_conjuge",
            "Número de filhos": "entry_n_filhos",  
            "Peso": "entry_peso",
            "Altura": "entry_altura",
            "Possui procuração": "cbox_procuracao",  
            "Quem possui procuração": "entry_procu_re",  
            "Possui curatela": "cbox_cura",  
            "Quem é responsável pela curatela": "entry_resp_cura", 
            "Diagnóstico atual(ais)": "entry_diag",
            "Outras doenças associadas": "entry_cultura_lazer",  
            "Alergias": "entry_alergia",
            "Escolaridade": "entry_escolaridade",
            "Deficiências físicas associadas": "cbox_deficiencia",
            "Faz uso de": "cbox_uso",
            "Qual outro": "entry_uso_outro",
            "Diagnósticos": "entry_diagnostico",
            "Grau dependência": "entry_depen", 
            "Motivo da opção pela moradia": "entry_motivo_moradia",
            "Benefício": "cbox_beneficio",
            "Morador administra seus recursos": "cbox_recursos",  
            "Manutenção do morador paga por": "cbox_pagamento",
            "Breve histórico do morador(a)": "entry_historico",
            "Relação morador com a casa": "entry_rel_com",  
            "Potencialidades": "entry_poten",
            "Condição de autonomia": "cbox_cond",
            "Visão equipe relação família": "entry_rel_morador",  
            "Planejamento para estreitamento da relação familiar": "entry_rel_plano",
            "Atividades, frequência e objetivo": "entry_rel_atividades",
            "Representante legal": "cbox_representante",
            "Locomoção": "entry_rel_ambulacao",
            "Há contato com familiares?": "entry_contatof",
            "Como é relação do residente com a família?": "entry_re_familia",
            "Recebe visitas? Quem?": "entry_rel_visita",
            "Possibilidade de reintegração familiar": "entry_reintegrar",  
            "Visita familiares?": "entry_visita", 
            "Recebe/faz ligações telefônicas": "entry_telefonemas",  
            "Aceita tomar medicação": "entry_aceita_medica",  
            "Aceita outros tratamentos": "entry_outros_medica", 
            "Acompanhamento externo em instituição de saúde": "entry_acom_exter",
            "Trânsito pela instituição": "cbox_transitar",
            "Alteração observada na autonomia": "entry_alt_autonomia"
        }
        if dados_cadastros and isinstance(dados_cadastros, dict):
            for campo, valor in dados_cadastros.items():
                entry_name = mapeamento.get(campo) 
                if entry_name:
                    entry = getattr(self, entry_name, None)                  
                    if entry:

                        if isinstance(entry, CTkComboBox):
                            entry.set(valor)
                        elif isinstance(entry, CTkEntry):
                            entry.delete(0, 'end') 
                            entry.insert(0, valor)


        
        

        self.button_contato = CTkButton(scrollable_frame2, text="Gerenciar contatos", command=self.editar_contatos)
        self.button_contato.pack(pady=20)

        self.button_contato = CTkButton(scrollable_frame2, text="Gerenciar medicamentos", command=self.gerenciar_medicamentos)
        self.button_contato.pack(pady=20)

        self.button_fechar = CTkButton(scrollable_frame2, text="Fechar", command=lambda: (root.deiconify(), janela_cadastro.withdraw()))
        self.button_fechar.pack(pady=20)


        btn_salvar = CTkButton(scrollable_frame2, text="Salvar", command=self.salvar_dados)
        btn_salvar.pack(pady=20)
        janela_cadastro.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), janela_cadastro.withdraw()))        
        janela_cadastro.mainloop()

    def limpar_campos(self):

        for campo in [
            "entry_nome", "entry_data_nascimento", "entry_data_entrada", "entry_RG",
            "entry_CPF", "entry_endereço_anterior", "entry_estado_civil", "entry_nome_conjuge",
            "entry_n_filhos", "entry_peso", "entry_altura", "cbox_procuracao",
            "entry_procu_re", "cbox_cura", "entry_resp_cura", "entry_diag",
            "cbox_depen", "entry_cultura_lazer", "entry_alergia", "entry_escolaridade",
            "cbox_deficiencia", "cbox_uso", "entry_uso_outro", "entry_diagnostico",
            "entry_depen", 
            "entry_motivo_moradia", "cbox_beneficio", "entry_qual_b", "cbox_recursos",
            "entry_recursos_q", "cbox_pagamento", "entry_historico", "entry_rel_com",
            "entry_poten", "cbox_cond", "entry_rel_familia", "entry_rel_morador",
            "entry_rel_plano", "entry_rel_atividades", "cbox_representante", "entry_rel_ambulacao",
            "entry_rel_visita", "entry_contatof", "entry_reintegrar", "entry_visita",
            "entry_telefonemas", "entry_aceita_medica", "entry_outros_medica", "entry_acom_exter",
            "entry_alt_autonomia"
            ]:
            entry = getattr(self, campo, None)
            if isinstance(entry, CTkEntry):
                entry.delete(0, 'end') 
            elif isinstance(entry, CTkComboBox):
                entry.set("")

    def converter_para_numero(self, text):
        try:
            return float(text.replace(",", "."))
        except ValueError:
            return None
        
    def calcular_imc(self):
        peso = self.converter_para_numero(self.entry_peso.get())
        altura = self.converter_para_numero(self.entry_altura.get())
        if peso and altura:
            altura /= 100  # Converte altura de cm para metros
            imc = peso / (altura ** 2)
            classificacao_imc = self.classificar_imc(imc)
            self.label_imc.configure(text=f"IMC: {imc:.2f} - {classificacao_imc}")
            return imc, classificacao_imc
        else:
            self.label_imc.configure(text="")
            return None, None
        
    def formatar_data_nascimento(self, event=None):
        texto = self.entry_data_nascimento.get().replace("/", "")
        novo_texto = ""
        if len(texto) >= 2:
            novo_texto += texto[:2] + "/"
        if len(texto) >= 4:
            novo_texto += texto[2:4] + "/"
        novo_texto += texto[4:]
        pos_cursor = self.entry_data_nascimento.index(INSERT)
        if novo_texto != self.entry_data_nascimento.get():
            self.entry_data_nascimento.delete(0, END)
            self.entry_data_nascimento.insert(0, novo_texto)
            if pos_cursor < 2:
                self.entry_data_nascimento.icursor(pos_cursor)
            elif pos_cursor < 4:
                self.entry_data_nascimento.icursor(pos_cursor + 1)
            elif pos_cursor < 6:
                self.entry_data_nascimento.icursor(pos_cursor + 2)
            else:
                pass

    def formatar_data_entrada(self, event=None):
        texto = self.entry_data_entrada.get().replace("/", "")
        novo_texto = ""
        if len(texto) >= 2:
            novo_texto += texto[:2] + "/"
        if len(texto) >= 4:
            novo_texto += texto[2:4] + "/"
        novo_texto += texto[4:]
        pos_cursor = self.entry_data_entrada.index(INSERT)
        if novo_texto != self.entry_data_entrada.get():
            self.entry_data_entrada.delete(0, END)
            self.entry_data_entrada.insert(0, novo_texto)
            if pos_cursor < 2:
                self.entry_data_entrada.icursor(pos_cursor)
            elif pos_cursor < 4:
                self.entry_data_entrada.icursor(pos_cursor + 1)
            elif pos_cursor < 6:
                self.entry_data_entrada.icursor(pos_cursor + 2)
            else:
                self.entry_data_entrada.icursor(len(novo_texto))

    def editar_contatos(self):
        self.janela_contatos = CTkToplevel(self.root)
        self.janela_contatos.title("Editar Contatos")

        self.entry_nome_contato = CTkEntry(self.janela_contatos, placeholder_text="Nome do Contato")
        self.entry_nome_contato.pack()

        self.entry_numero_telefone = CTkEntry(self.janela_contatos, placeholder_text="(xx)xxxxxxxxxx")
        self.entry_numero_telefone.pack()
        self.entry_numero_telefone.bind("<KeyRelease>", self.formatar_telefone)

        botao_adicionar_contato = CTkButton(self.janela_contatos, text="Adicionar Contato", command=self.adicionar_contato)
        botao_adicionar_contato.pack()

        self.listbox_contatos = tk.Listbox(self.janela_contatos)
        self.listbox_contatos.pack(fill=tk.BOTH, expand=True)

        self.label_contatos = CTkLabel(self.janela_contatos, text="")
        self.label_contatos.pack()

        botao_gerenciar_contato = CTkButton(self.janela_contatos, text="Gerenciar Contato", command=self.gerenciar_contato)
        botao_gerenciar_contato.pack()

        botao_excluir_contato = CTkButton(self.janela_contatos, text="Excluir Contato", command=self.excluir_contato)
        botao_excluir_contato.pack()

        botao_fechar = CTkButton(self.janela_contatos, text="Fechar", command=self.janela_contatos.destroy)
        botao_fechar.pack(pady=10)

        self.atualizar_lista_contatos()

    def formatar_telefone(self, event):
        numero = self.entry_numero_telefone.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            
        if len(numero) > 2:
            numero = f"({numero[:2]}){numero[2:]}"
        if len(numero) > 9:
            numero = f"{numero[:9]}-{numero[9:]}"
            
        self.entry_numero_telefone.delete(0, tk.END)
        self.entry_numero_telefone.insert(0, numero)

    def adicionar_contato(self):
        nome = self.entry_nome_contato.get()
        telefone = self.entry_numero_telefone.get()
        if nome and telefone:
            self.contatos.append((nome, telefone))
            self.atualizar_lista_contatos()
            self.entry_nome_contato.delete(0, tk.END)
            self.entry_numero_telefone.delete(0, tk.END)

    def atualizar_lista_contatos(self):
        self.listbox_contatos.delete(0, tk.END)
        for contato in self.contatos:
            self.listbox_contatos.insert(tk.END, f"{contato[0]} - {contato[1]}")

    def gerenciar_contato(self):
        try:
            indice_selecionado = self.listbox_contatos.curselection()[0]
            contato_selecionado = self.contatos[indice_selecionado]

            self.entry_nome_contato.delete(0, tk.END)
            self.entry_nome_contato.insert(0, contato_selecionado[0])
            self.entry_numero_telefone.delete(0, tk.END)
            self.entry_numero_telefone.insert(0, contato_selecionado[1])

            self.contatos.pop(indice_selecionado)
            self.atualizar_lista_contatos()
        except IndexError:
            self.label_contatos.configure(text="Selecione um contato para gerenciar.")

    def excluir_contato(self):
        try:
            indice_selecionado = self.listbox_contatos.curselection()[0]
            self.contatos.pop(indice_selecionado)
            self.atualizar_lista_contatos()
        except IndexError:
            self.label_contatos.configure(text="Selecione um contato para excluir.")

    def gerenciar_medicamentos(self):
        janela_gerenciamento = CTkToplevel()
        janela_gerenciamento.title("Gerenciar Medicamentos")


        self.medicamentos_listbox = tk.Listbox(janela_gerenciamento, width=50, height=10)
        self.medicamentos_listbox.pack(pady=10)


        self.atualizar_lista_medicamentos()


        adicionar_btn = CTkButton(janela_gerenciamento, text="Adicionar Medicamento",
                                       command=lambda: self.adicionar_medicamento(janela_gerenciamento))
        adicionar_btn.pack(pady=5)

        editar_btn = CTkButton(janela_gerenciamento, text="Editar Medicamento",
                                    command=lambda: self.editar_medicamento_selecionado(janela_gerenciamento))
        editar_btn.pack(pady=5)

        excluir_btn = CTkButton(janela_gerenciamento, text="Excluir Medicamento", command=self.excluir_medicamento_selecionado)
        excluir_btn.pack(pady=5)


        fechar_btn = CTkButton(janela_gerenciamento, text="Fechar", command=janela_gerenciamento.destroy)
        fechar_btn.pack(pady=5)
        janela_gerenciamento.deiconify()

    def atualizar_lista_medicamentos(self):
        self.medicamentos_listbox.delete(0, "end")
        for medicamento in self.medicamentos:

            self.medicamentos_listbox.insert("end", 
                f"{medicamento[0]} - {medicamento[1]} unidade(s), {medicamento[2]} dosagem, horário: {medicamento[3]}")

    def adicionar_medicamento(self, janela):
        janela_medicamento = CTkToplevel()
        janela_medicamento.title("Adicionar Medicamento")
        CTkLabel(janela_medicamento, text="Nome do Medicamento:").pack(pady=5)
        nome_entry = CTkEntry(janela_medicamento)
        nome_entry.pack(pady=5)

        CTkLabel(janela_medicamento, text="Quantidade:").pack(pady=5)
        quantidade_entry = CTkEntry(janela_medicamento)
        quantidade_entry.pack(pady=5)

        CTkLabel(janela_medicamento, text="Dosagem:").pack(pady=5)
        dosagem_entry = CTkEntry(janela_medicamento)
        dosagem_entry.pack(pady=5)

        CTkLabel(janela_medicamento, text="Horário:").pack(pady=5)
        horario_entry = CTkEntry(janela_medicamento)
        horario_entry.pack(pady=5)

        adicionar_btn = CTkButton(janela_medicamento, text="Adicionar",
                                command=lambda: self.salvar_medicamento(nome_entry.get(),
                                                                            quantidade_entry.get(),
                                                                            dosagem_entry.get(),
                                                                            horario_entry.get(),
                                                                            janela_medicamento))
        adicionar_btn.pack(pady=10)
        janela.iconify()

    def salvar_medicamento(self, nome, quantidade, dosagem, horario, janela):
        if nome and quantidade and dosagem and horario:
            medicamento = (nome, quantidade, dosagem, horario)
            self.medicamentos.append(medicamento)
            self.atualizar_lista_medicamentos()
            janela.destroy()
            self.janela_gerenciamento.deiconify()

    def editar_medicamento_selecionado(self, janela):
        selecionado = self.medicamentos_listbox.curselection()  
        if selecionado:
            index = selecionado[0] 
            self.editar_medicamento(index)  

    def editar_medicamento(self, janela, index):
        medicamento = self.medicamentos[index]

        janela_editar = CTkToplevel()
        janela_editar.title("Editar Medicamento")


        CTkLabel(janela_editar, text="Nome do Medicamento:").pack(pady=5)
        nome_entry = CTkEntry(janela_editar)
        nome_entry.insert(0, medicamento[0])
        nome_entry.pack(pady=5)

        CTkLabel(janela_editar, text="Quantidade:").pack(pady=5)
        quantidade_entry = CTkEntry(janela_editar)
        quantidade_entry.insert(0, medicamento[1])
        quantidade_entry.pack(pady=5)

        CTkLabel(janela_editar, text="Dosagem:").pack(pady=5)
        dosagem_entry = CTkEntry(janela_editar)
        dosagem_entry.insert(0, medicamento[2])
        dosagem_entry.pack(pady=5)

        CTkLabel(janela_editar, text="Horário:").pack(pady=5)
        horario_entry = CTkEntry(janela_editar)
        horario_entry.insert(0, medicamento[3])
        horario_entry.pack(pady=5)

        salvar_editar_btn = CTkButton(janela_editar, text="Salvar",
                                    command=lambda: self.salvar_edicao_medicamento(index, nome_entry.get(),
                                                                                    quantidade_entry.get(),
                                                                                    dosagem_entry.get(),
                                                                                    horario_entry.get(),
                                                                                    janela_editar))
        salvar_editar_btn.pack(pady=10)
        janela.iconify()

    def excluir_medicamento_selecionado(self):
        selecionado = self.medicamentos_listbox.curselection() 
        if selecionado:
            index = selecionado[0]  
            del self.medicamentos[index]  
            self.atualizar_lista_medicamentos()  

    def salvar_dados(self):
        medicamentos_str = "; ".join([f"{med[0]} - {med[1]} unidade(s), {med[2]} dosagem, horário: {med[3]}" for med in self.medicamentos])
        contatos_str = "; ".join([f"{contato[0]} - {contato[1]}" for contato in self.contatos])
        
        dados_do_morador_pia = {
            "Nome do residente": self.entry_nome.get(),
            "Data de nascimento": self.entry_data_nascimento.get(),
            "Data de entrada": self.entry_data_entrada.get(),
            "RG": self.entry_RG.get(),
            "CPF": self.entry_CPF.get(),
            "Endereço Anterior": self.entry_endereço_anterior.get(),
            "Estado Civil": self.entry_estado_civil.get(),
            "Nome do cônjuge": self.entry_nome_conjuge.get(),
            "Número de filhos": self.entry_n_filhos.get(),
            "Peso": self.entry_peso.get(),
            "Altura": self.entry_altura.get(),
            "Possui procuração": self.cbox_procuracao.get(),
            "Quem possui procuração": self.entry_procu_re.get(),
            "Possui curatela": self.cbox_cura.get(),
            "Quem é responsável pela curatela": self.entry_resp_cura.get(),
            "Diagnóstico atual(ais)": self.entry_diag.get(),
            "Outras doenças associadas": self.entry_cultura_lazer.get(),
            "Alergias": self.entry_alergia.get(),
            "Escolaridade": self.entry_escolaridade.get(),
            "Deficiências físicas associadas": self.cbox_deficiencia.get(),
            "Faz uso de": self.cbox_uso.get(),
            "Qual outro": self.entry_uso_outro.get(),
            "Diagnósticos": self.entry_diagnostico.get(),
            "Grau dependência": self.cbox_depen.get(),
            "Motivo da opção pela moradia": self.entry_motivo_moradia.get(),
            "Benefício": self.cbox_beneficio.get(),
            "Morador administra seus recursos": self.cbox_recursos.get(),
            "Manutenção do morador paga por": self.cbox_pagamento.get(),
            "Breve histórico do morador(a)": self.entry_historico.get(),
            "Relação morador com a casa": self.entry_rel_com.get(),
            "Potencialidades": self.entry_poten.get(),
            "Condição de autonomia": self.cbox_cond.get(),
            "Visão equipe relação família": self.entry_rel_morador.get(),
            "Planejamento para estreitamento da relação familiar": self.entry_rel_plano.get(),
            "Atividades, frequência e objetivo": self.entry_rel_atividades.get(),
            "Representante legal": self.cbox_representante.get(),
            "Locomoção": self.entry_rel_ambulacao.get(),
            "Recebe visitas? Quem?": self.entry_rel_visita.get(),
            "Possibilidade de reintegração familiar": self.entry_reintegrar.get(),
            "Visita familiares?": self.entry_visita.get(),
            "Recebe/faz ligações telefônicas": self.entry_telefonemas.get(),
            "Aceita tomar medicação": self.entry_aceita_medica.get(),
            "Aceita outros tratamentos": self.entry_outros_medica.get(),
            "Acompanhamento externo em instituição de saúde": self.entry_acom_exter.get(),
            "Trânsito pela instituição": self.cbox_transitar.get(),
            "Alteração observada na autonomia": self.entry_alt_autonomia.get(),
            "Há contato com familiares?": self.entry_contatof.get(),
            "Como é relação do residente com a família?": self.entry_re_familia.get(),
            "Medicamentos": medicamentos_str,
            "Contatos": contatos_str
        }

        dados_do_morador_cadastro = {
            "Nome do residente": self.entry_nome.get(),
            "Data de nascimento": self.entry_data_nascimento.get(),
            "Data de entrada": self.entry_data_entrada.get(),
            "RG": self.entry_RG.get(),
            "CPF": self.entry_CPF.get(),
            "Endereço Anterior": self.entry_endereço_anterior.get(),
            "Estado Civil": self.entry_estado_civil.get(),
            "Nome do cônjuge": self.entry_nome_conjuge.get(),
            "Número de filhos": self.entry_n_filhos.get(),
            "Motivo da opção pela moradia": self.entry_motivo_moradia.get(),
            "Benefício": self.cbox_beneficio.get(),
            "Qual?": self.entry_qual_b.get(),
            "Morador administra seus recursos financeiros?": self.cbox_recursos.get(),
            "Quem exerce isso para ele?": self.entry_recursos_q.get(),
            "A manutenção do morador na instituição é paga por": self.cbox_pagamento.get(),
            "Breve histórico do morador(a)": self.entry_historico.get(),
            "Alergias ou intolerâncias": self.entry_alergia.get(),
            "Condição de autonomia": self.cbox_cond.get(),
            "Atividades, frequência e objetivo": self.entry_rel_atividades.get(),
            "Representante legal": self.cbox_representante.get(),
            "Medicamentos": medicamentos_str,
            "Contatos": contatos_str
        }

        self.dados_salvos = {
            "PIA": dados_do_morador_pia,
            "Cadastro": dados_do_morador_cadastro
        }
        self.manager.salvar_casa_apoio(dados_do_morador_pia, dados_do_morador_cadastro)
        self.limpar_campos()
        CTkMessagebox(title="Sucesso!", message="Morador cadastrado!", icon="check")

    def finalizar_cadastro(self):

        if not self.entry_nome.get():  
            CTkMessagebox(title="Erro", message="Erro! Nome do residente é obrigatório.", icon="cancel")
            return


        self.manager.salvar_casa_apoio(self.dados_salvos["PIA"], self.dados_salvos["Cadastro"])
        CTkMessagebox(title="Sucesso", message="Morador cadastrado com sucesso!", icon="check")

    def build_ui(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_dir, 'icons')
        vo_iza_path = os.path.join(base_dir, 'Vó iza')

        button_width = 150
        button_height = 50

        frame = CTkFrame(master=root, fg_color="#4d4dae", border_color="#00008b", border_width=2)
        frame.pack(side="left", fill="y", padx=10, pady=10)

        casa_imagem = Image.open(os.path.join(icon_path, "house.png"))
        casa_imagem = CTkImage(casa_imagem)
        botao_cadastrar_pia = CTkButton(master=frame, font=("Calibri", 15), text="Cadastrar Morador", 
                                        height=button_height, width=button_width, image=casa_imagem, 
                                        command=self.cadastro_casa_apoio, )
        botao_cadastrar_pia.pack(padx=10, pady=10)

        management_imagem = Image.open(os.path.join(icon_path, "management.png"))
        management_imagem = CTkImage(management_imagem)
        botao_editar_casa = CTkButton(master=frame, font=("Calibri", 15), text="Gerenciar Morador", 
                                    height=button_height, width=button_width, image=management_imagem, 
                                    command=self.leitor.abrir_janela_edicao)
        botao_editar_casa.pack(padx=10, pady=10)

        botao_download_pdf = CTkButton(master=frame, font=("Calibri", 15), text="Download PIA", 
                                    height=button_height, width=button_width, image=management_imagem, command=self.pdf.abrir_janela_download)
        botao_download_pdf.pack(padx=10, pady=10)

        frame_superior = CTkFrame(master=root, fg_color="#f0f0f0", width=200, height=200)
        frame_superior.place(x=215, y=10)

        vo_iza_imagem = Image.open(os.path.join(vo_iza_path, "vo iza.jpeg"))
        vo_iza_imagem = CTkImage(vo_iza_imagem, size=(360, 180))
        label_imagem = CTkLabel(master=frame_superior, image=vo_iza_imagem, text="")
        label_imagem.pack(pady=10, padx=10)
   

        frame_inferior_direito = CTkFrame(master=root, fg_color="#f0f0f0")
        frame_inferior_direito.place(relx=1, rely=1, anchor="se", x=-10, y=-10)  # Ajuste x e y para o padding

        disclaimer_text = "Apoio Fácil é um software livre!\n" \
                        "Venda proibida. Distribuído gratuitamente."
        
        label_disclaimer = CTkLabel(master=frame_inferior_direito, text=disclaimer_text, 
                                    font=("Calibri", 12), fg_color="#4d4dae", text_color="white")
        label_disclaimer.pack(padx=10, pady=10)

class LeitorDadosCasaApoio:
    def __init__(self, data_directory, app_instance):
        self.data_directory = data_directory
        self.pasta_cadastros = os.path.join(self.data_directory, "cadastros registro admissional")
        self.pasta_PIA = os.path.join(self.data_directory, "PIA")
        self.app_instance = app_instance 
        self.root = root

    def ler_dados_cadastros(self):
        dados = []
        cadastro_arquivo = os.path.join(self.pasta_PIA, "data_pia.csv")

        if os.path.exists(cadastro_arquivo):
            with open(cadastro_arquivo, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    dados.appe(row)
        return dados
        
    def ler_dados_pia(self):
        dados1 = []
        pia_arquivo = os.path.join(self.pasta_PIA, "data_pia.csv")

        if os.path.exists(pia_arquivo):
            with open(pia_arquivo, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    dados1.append(row)
        return dados1

    def abrir_janela_edicao(self):
        dados_cadastros = self.ler_dados_pia()
        janela_edicao = CTkToplevel()  
        janela_edicao.title("Edição de Dados")
        janela_edicao.geometry("600x400")
        janela_edicao.resizable(False, False)
        self.root.iconify()

        def restaurar_janela_principal():
            self.root.deiconify()  
            janela_edicao.destroy()  

        janela_edicao.protocol("WM_DELETE_WINDOW", restaurar_janela_principal)


        self.listbox_dados = CTkListbox(
            janela_edicao,
            width=500,  
            height=300,  
            fg_color="white",  
            border_color="black",  
            text_color="black",  
            hover_color="#f0f0f0", 
        )
        self.listbox_dados.pack(fill="both", expand=True)

        if dados_cadastros:
            for dado in dados_cadastros:
                nome_morador = dado.get("Nome do residente", "Sem nome") 
                self.listbox_dados.insert(END, nome_morador)  

        btn_abrir_cadastro = CTkButton(
            janela_edicao, 
            text="Abrir cadastro do residente", 
            command=lambda: [self.abrir_dados_selecionados(), janela_edicao.withdraw()]
        )
        btn_abrir_cadastro.pack(pady=10)

        btn_excluir_dado = CTkButton(
            janela_edicao, 
            text="Excluir cadastro do residente", 
            command=self.excluir_dado_selecionado
        )
        btn_excluir_dado.pack(pady=5)

    def abrir_dados_selecionados(self):
        selecionado = selecionado = self.listbox_dados.get(self.listbox_dados.curselection())        
        if selecionado:
            dados_cadastros = self.ler_dados_pia() 
            morador_dados = next((dado for dado in dados_cadastros if dado.get("Nome do residente") == selecionado), None)        
            if morador_dados:
                if hasattr(self.app_instance, 'cadastro_casa_apoio'):
                    self.app_instance.cadastro_casa_apoio(morador_dados)

    def excluir_dado_selecionado(self):
        selecionado = self.listbox_dados.curselection()
        if selecionado:
            idx = selecionado[0] if isinstance(selecionado, (tuple, list)) else selecionado
            nome_morador = self.listbox_dados.get(idx)
            dados_cadastros = self.ler_dados_cadastros()
            morador_dados = next((dado for dado in dados_cadastros if dado.get("Nome do residente") == nome_morador), None)
            
            if morador_dados:
                self.listbox_dados.delete(idx)
                self.excluir_dado_do_csv(nome_morador)
       
    def excluir_dado_do_csv(self, nome_morador):
        dados_cadastros = self.ler_dados_cadastros()
        dados_atualizados = [dado for dado in dados_cadastros if dado.get("Nome do residente") != nome_morador]
        cadastro_arquivo = os.path.join(self.pasta_PIA, "data_pia.csv")
        
        if os.path.exists(cadastro_arquivo):
            with open(cadastro_arquivo, mode='w', newline='', encoding='utf-8') as file:
                if dados_atualizados:
                    writer = csv.DictWriter(file, fieldnames=dados_atualizados[0].keys())
                    writer.writeheader()
                    writer.writerows(dados_atualizados)
                else:
                    file.truncate()

    def salvar_dados_atualizados(self, idx, key, novo_valor):
        cadastro_arquivo = os.path.join(self.pasta_pia, "data_pia.csv")
        if os.path.exists(cadastro_arquivo):
            dados = self.ler_dados_cadastros()
            dados[idx][key] = novo_valor  
            with open(cadastro_arquivo, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=dados[0].keys())
                writer.writeheader()
                writer.writerows(dados)

class GeradorPDF:
    def __init__(self, data_directory, app_instance):
        self.data_directory = data_directory
        self.app_instance = app_instance
        self.leitor = LeitorDadosCasaApoio(data_directory, app_instance)
        self.pasta_cadastros = os.path.join(self.data_directory, "cadastros registro admissional")
        self.pasta_PIA = os.path.join(self.data_directory, "PIA")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.vo_iza_path = os.path.join(base_dir, 'Vó iza') 

    def adicionar_imagem(self, c):
        vo_iza_imagem = utils.ImageReader(os.path.join(self.vo_iza_path, "vo iza.jpeg"))
        width, height = vo_iza_imagem.getSize()
        c.drawImage(vo_iza_imagem, 200 , 700, width=180, height=100)


    def adicionar_imagem_e_texto(self, c): 
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 650, "PLANO INDIVIDUAL DE ATENDIMENTO")
        c.setFont("Helvetica", 10)
        c.drawString(100, 635, "DADOS GERAIS DA INSTITUIÇÃO")
        c.drawString(100, 620, "Nome da Instituição: Casa de apoio Vó Iza")
        c.drawString(100, 600, "CNPJ: 30.820.946/0001-65")
        c.drawString(100, 580, "Endereço: Rua Major Theolindo Ferreira Ribas, 2960 – Boqueirão")


    def gerar_pdf_cadastro(self, morador_dados):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{morador_dados['Nome do residente']}_cadastro.pdf"
        )

        if save_path:
            c = canvas.Canvas(save_path, pagesize=letter)
            self.adicionar_imagem(c)
            y_position = self.adicionar_imagem_e_texto(c)  
            

            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, 550, "DADOS DO MORADOR(A)")
            y_position = 500  
            
            c.setFont("Helvetica", 10)

            for key, value in morador_dados.items():
                text = f"{key}: {value}"
                

                if y_position < 110: 
                    c.showPage()
                    self.adicionar_imagem(c)  
                    c.setFont("Helvetica", 10)  
                    y_position = 580 


                if c.stringWidth(text, "Helvetica", 10) > (letter[0] - 200):  
                    for line in textwrap.wrap(text, width=50):  
                        c.drawString(100, y_position, line)
                        y_position -= 12  
                else:
                    c.drawString(100, y_position, text)
                    y_position -= 20  


            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, 100, "RESPONSÁVEL PELAS INFORMAÇÕES:")
            c.setFont("Helvetica", 10)
            c.drawString(100, 80, "Nome do profissional: Lorenna Donini Oliveira")
            c.drawString(100, 60, "Função: responsável técnica")
            c.drawString(100, 40, f"Curitiba, {datetime.now().strftime('%d/%m/%Y')}")
            
            c.save()  
            return save_path
        return None

    def gerar_pdf_pia(self, dados_morador):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{dados_morador['Nome do residente']}_PIA.pdf"
        )
        if save_path:
            c = canvas.Canvas(save_path, pagesize=letter)
            self.adicionar_imagem(c)
            y_position = self.adicionar_imagem_e_texto(c)  
            

            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, 550, "DADOS DO MORADOR(A)")
            y_position = 500  
            
            c.setFont("Helvetica", 10)

            for key, value in dados_morador.items():
                text = f"{key}: {value}"
                

                if y_position < 110: 
                    c.showPage()
                    self.adicionar_imagem(c)  
                    c.setFont("Helvetica", 10)  
                    y_position = 580 


                if c.stringWidth(text, "Helvetica", 10) > (letter[0] - 200):  
                    for line in textwrap.wrap(text, width=50):  
                        c.drawString(100, y_position, line)
                        y_position -= 12  
                else:
                    c.drawString(100, y_position, text)
                    y_position -= 20  


            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, 100, "RESPONSÁVEL PELAS INFORMAÇÕES:")
            c.setFont("Helvetica", 10)
            c.drawString(100, 80, "Nome do profissional: Lorenna Donini Oliveira")
            c.drawString(100, 60, "Função: responsável técnica")
            c.drawString(100, 40, f"Curitiba, {datetime.now().strftime('%d/%m/%Y')}")
            
            c.save()  
            return save_path
        return None

    def abrir_janela_download(self):
        dados_cadastros = self.leitor.ler_dados_cadastros()
        root.iconify()

        janela_download = CTkToplevel()
        janela_download.title("Download de PDF")
        janela_download.geometry("400x300")

        listbox_dados = tk.Listbox(janela_download)
        listbox_dados.pack(fill=tk.BOTH, expand=True)

        for dado in dados_cadastros:
            nome_morador = dado.get("Nome do residente", "Sem nome")
            listbox_dados.insert(tk.END, nome_morador)

        btn_download_cadastro = CTkButton(
            janela_download,
            text="Download PDF Cadastro Admissional",
            command=lambda: self.download_pdf_selecionado(listbox_dados, tipo_relatorio="cadastro")
        )
        btn_download_cadastro.pack(pady=10)

        btn_download_pia = CTkButton(
            janela_download,
            text="Download PDF Relatório PIA",
            command=lambda: self.download_pdf_selecionado(listbox_dados, tipo_relatorio="pia")
        )
        btn_download_pia.pack(pady=10)
        janela_download.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), janela_download.withdraw()))    

    def download_pdf_selecionado(self, listbox_dados, tipo_relatorio):
        selecionado_index = listbox_dados.curselection()
        if not selecionado_index:
            ctkmessagebox()
            return

        nome_morador = listbox_dados.get(selecionado_index)

        morador_dados = next(
            (dado for dado in self.leitor.ler_dados_cadastros() if dado.get("Nome do residente") == nome_morador),
            None
        )

        if morador_dados is None:
            print(f"Dados do residente '{nome_morador}' não encontrados.")
            return

        if tipo_relatorio == "cadastro":
            pdf_path = self.gerar_pdf_cadastro(morador_dados)
            print(f"PDF do Cadastro Admissional gerado em: {pdf_path}")
        elif tipo_relatorio == "pia":
            pdf_path = self.gerar_pdf_pia(morador_dados)
            print(f"PDF do Relatório PIA gerado em: {pdf_path}")


if __name__ == "__main__":
    root = CTk()
    app = CasaApoioApp(root)
    root.mainloop()
