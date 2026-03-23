import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Gestão Clínica Odontológica 🦷"
    page.bgcolor = "#121212" 
    page.padding = 15
    page.horizontal_alignment = "center"
    page.scroll = "auto" # Libera a rolagem da tela no celular

    # --- DADOS DO SISTEMA ---
    dados = {
        "d1_nome": "", "d2_nome": "", 
        "d1_saldo": 0.0, "d2_saldo": 0.0, 
        "d1_bruto": 0.0, "d2_bruto": 0.0, 
        "d1_qtd": 0, "d2_qtd": 0, 
        "d1_ativo": True, "d2_ativo": True,
        "taxa": 0.15, 
        "total_geral": 0.0 
    }

    def mostrar_mensagem(texto, cor):
        snack = ft.SnackBar(ft.Text(texto, color="white", weight="bold"), bgcolor=cor)
        page.snack_bar = snack
        snack.open = True
        page.update()

    # --- COMPONENTES VISUAIS (AJUSTADOS PARA LARGURA DE CELULAR) ---
    largura_celular = 320 # Tamanho seguro que cabe em qualquer smartphone

    txt_nome_d1 = ft.TextField(label="Nome do Dentista 1", width=largura_celular, bgcolor="#1E1E1E", border_color="#00ADB5")
    txt_nome_d2 = ft.TextField(label="Nome do Dentista 2", width=largura_celular, bgcolor="#1E1E1E", border_color="#00ADB5")

    txt_valor = ft.TextField(
        label="Valor Cobrado (R$)", 
        keyboard_type="number", 
        width=largura_celular, 
        bgcolor="#1E1E1E", 
        border_color="#00ADB5",
        text_size=20
    )
    
    lbl_taxa = ft.Text("Rateio Atual: 15%", size=16, color="#00ADB5", weight="bold")
    
    # Painel de Resumo do Caixa
    lbl_total_bruto = ft.Text("Faturamento Bruto: R$ 0.00", size=14, color="#888888")
    lbl_total_comissoes = ft.Text("Comissões (Doutores): R$ 0.00", size=14, color="#FF4444")
    lbl_saldo_clinica = ft.Text("Caixa Líquido: R$ 0.00", size=20, color="#00C851", weight="bold")
    
    lbl_d1_display = ft.Text("Dentista A", size=18, weight="bold", color="white")
    lbl_d1_saldo_display = ft.Text("R$ 0.00", size=22, weight="bold", color="#00ADB5")
    lbl_d1_status = ft.Text("🟢 Ativo", color="#00C851", size=14)
    
    lbl_d2_display = ft.Text("Dentista B", size=18, weight="bold", color="white")
    lbl_d2_saldo_display = ft.Text("R$ 0.00", size=22, weight="bold", color="#00ADB5")
    lbl_d2_status = ft.Text("🟢 Ativo", color="#00C851", size=14)
    
    lista_historico = ft.ListView(expand=False, spacing=10, height=250)

    # --- LÓGICA DO SISTEMA ---
    def atualizar_tela():
        ativos = sum([dados["d1_ativo"], dados["d2_ativo"]])
        dados["taxa"] = 0.30 if ativos == 1 else 0.15
        lbl_taxa.value = f"Rateio Atual: {dados['taxa']*100:.0f}%"
        lbl_taxa.color = "#FFBB33" if dados["taxa"] == 0.30 else "#00ADB5"
        
        lbl_d1_display.value = dados["d1_nome"]
        lbl_d1_saldo_display.value = f"Comissão: R$ {dados['d1_saldo']:.2f}"
        lbl_d1_status.value = f"🟢 Ativo | {dados['d1_qtd']} Atend." if dados["d1_ativo"] else f"🔴 Fechado | {dados['d1_qtd']} Atend."
        lbl_d1_status.color = "#00C851" if dados["d1_ativo"] else "#FF4444"
        btn_sair1.visible = dados["d1_ativo"]
        
        lbl_d2_display.value = dados["d2_nome"]
        lbl_d2_saldo_display.value = f"Comissão: R$ {dados['d2_saldo']:.2f}"
        lbl_d2_status.value = f"🟢 Ativo | {dados['d2_qtd']} Atend." if dados["d2_ativo"] else f"🔴 Fechado | {dados['d2_qtd']} Atend."
        lbl_d2_status.color = "#00C851" if dados["d2_ativo"] else "#FF4444"
        btn_sair2.visible = dados["d2_ativo"]

        total_repasse = dados["d1_saldo"] + dados["d2_saldo"]
        liquido_clinica = dados["total_geral"] - total_repasse
        
        lbl_total_bruto.value = f"Faturamento Bruto: R$ {dados['total_geral']:.2f}"
        lbl_total_comissoes.value = f"Comissões (Doutores): R$ {total_repasse:.2f}"
        lbl_saldo_clinica.value = f"Caixa Líquido: R$ {liquido_clinica:.2f}"
        
        page.update()

    def sair_doc1(e):
        dados["d1_ativo"] = False
        atualizar_tela()

    def sair_doc2(e):
        dados["d2_ativo"] = False
        atualizar_tela()
        
    btn_sair1 = ft.TextButton("Encerrar Mapa", on_click=sair_doc1)
    btn_sair2 = ft.TextButton("Encerrar Mapa", on_click=sair_doc2)

    def estornar(e):
        reg = e.control.data
        dados["total_geral"] -= reg["valor"]
        
        if reg["d1_recebeu"]: 
            dados["d1_saldo"] -= reg["comissao"]
            dados["d1_bruto"] -= reg["valor"]
            dados["d1_qtd"] -= 1
        if reg["d2_recebeu"]: 
            dados["d2_saldo"] -= reg["comissao"]
            dados["d2_bruto"] -= reg["valor"]
            dados["d2_qtd"] -= 1
            
        lista_historico.controls.remove(reg["ui_row"])
        atualizar_tela()
        mostrar_mensagem("Estorno realizado com sucesso!", "#FFBB33")

    def lancar_procedimento(e):
        if not txt_valor.value: return
        try:
            v = float(txt_valor.value.replace(",", "."))
            if v <= 0: raise ValueError
            
            comissao = v * dados["taxa"]
            dados["total_geral"] += v 
            
            rec1 = dados["d1_ativo"]
            rec2 = dados["d2_ativo"]
            
            if rec1: 
                dados["d1_saldo"] += comissao
                dados["d1_bruto"] += v
                dados["d1_qtd"] += 1
            if rec2: 
                dados["d2_saldo"] += comissao
                dados["d2_bruto"] += v
                dados["d2_qtd"] += 1
            
            hora = datetime.now().strftime("%H:%M")
            reg = {"valor": v, "comissao": comissao, "d1_recebeu": rec1, "d2_recebeu": rec2}
            
            row_ui = ft.Container(
                content=ft.Row([
                    ft.Text(f"{hora}", color="#888888", size=12),
                    ft.Text(f"R$ {v:.2f}", weight="bold", color="white", size=16),
                    ft.TextButton("Desfazer", data=reg, on_click=estornar)
                ], alignment="spaceBetween"),
                bgcolor="#1E1E1E", padding=10, border_radius=8, width=largura_celular
            )
            
            reg["ui_row"] = row_ui
            lista_historico.controls.insert(0, row_ui)

            txt_valor.value = ""
            txt_valor.focus()
            atualizar_tela()
            mostrar_mensagem("Procedimento lançado!", "#00C851")
        except ValueError:
            mostrar_mensagem("Erro: Digite um valor numérico válido.", "#FF4444")

    def iniciar_clinica(e):
        dados["d1_nome"] = txt_nome_d1.value if txt_nome_d1.value else "Dentista A"
        dados["d2_nome"] = txt_nome_d2.value if txt_nome_d2.value else "Dentista B"
        painel_config.visible = False
        painel_caixa.visible = True
        atualizar_tela()

    def ir_para_fechamento(e):
        painel_caixa.visible = False
        painel_fechamento.visible = True
        
        total_repasse = dados["d1_saldo"] + dados["d2_saldo"]
        liquido_clinica = dados["total_geral"] - total_repasse

        lbl_rel_clinica.value = f"Caixa Líquido: R$ {liquido_clinica:.2f}"
        lbl_rel_bruto.value = f"Bruto Recebido: R$ {dados['total_geral']:.2f}"
        lbl_rel_comissoes.value = f"Comissões Pagas: R$ {total_repasse:.2f}"

        lbl_mapa_d1_nome.value = dados["d1_nome"]
        lbl_mapa_d1_qtd.value = f"Atendimentos: {dados['d1_qtd']}"
        lbl_mapa_d1_bruto.value = f"Produção Bruta: R$ {dados['d1_bruto']:.2f}"
        lbl_mapa_d1_repasse.value = f"Comissão: R$ {dados['d1_saldo']:.2f}"
        
        lbl_mapa_d2_nome.value = dados["d2_nome"]
        lbl_mapa_d2_qtd.value = f"Atendimentos: {dados['d2_qtd']}"
        lbl_mapa_d2_bruto.value = f"Produção Bruta: R$ {dados['d2_bruto']:.2f}"
        lbl_mapa_d2_repasse.value = f"Comissão: R$ {dados['d2_saldo']:.2f}"
        
        page.update()

    def resetar_e_voltar(e):
        dados["d1_saldo"] = 0.0; dados["d2_saldo"] = 0.0
        dados["d1_bruto"] = 0.0; dados["d2_bruto"] = 0.0
        dados["d1_qtd"] = 0; dados["d2_qtd"] = 0
        dados["total_geral"] = 0.0
        dados["d1_ativo"] = True; dados["d2_ativo"] = True
        lista_historico.controls.clear() 
        
        painel_fechamento.visible = False
        painel_config.visible = True
        page.update()

    def cancelar_fechamento(e):
        painel_fechamento.visible = False
        painel_caixa.visible = True
        page.update()

    # --- MONTAGEM DOS PAINÉIS (Tudo Empilhado para Mobile) ---
    
    painel_config = ft.Container(
        content=ft.Column([
            ft.Text("Gestão de Clínica", size=28, weight="bold", color="#00ADB5"),
            ft.Text("Configure os mapas", size=14, color="#888888"),
            ft.Divider(height=20, color="transparent"),
            txt_nome_d1, 
            txt_nome_d2,
            ft.Divider(height=10, color="transparent"),
            ft.ElevatedButton("Abrir Mapas do Dia", on_click=iniciar_clinica, width=largura_celular, height=50, bgcolor="#00ADB5", color="#121212")
        ], horizontal_alignment="center"),
    )

    card_d1 = ft.Container(
        content=ft.Column([lbl_d1_display, lbl_d1_saldo_display, lbl_d1_status, btn_sair1], horizontal_alignment="center", spacing=5),
        bgcolor="#1E1E1E", padding=15, border_radius=10, width=largura_celular
    )
    
    card_d2 = ft.Container(
        content=ft.Column([lbl_d2_display, lbl_d2_saldo_display, lbl_d2_status, btn_sair2], horizontal_alignment="center", spacing=5),
        bgcolor="#1E1E1E", padding=15, border_radius=10, width=largura_celular
    )

    painel_caixa = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Text("Mapas Abertos", size=24, weight="bold", color="#00ADB5"),
            lbl_taxa,
            ft.Divider(color="#333333", height=10),
            
            # Resumo Central
            ft.Container(
                content=ft.Column([
                    lbl_saldo_clinica,
                    ft.Divider(color="#333333"),
                    lbl_total_bruto, 
                    lbl_total_comissoes
                ], horizontal_alignment="center"),
                bgcolor="#1E1E1E", padding=15, border_radius=10, width=largura_celular
            ),
            
            ft.Divider(color="transparent", height=10),
            
            # Cartões Empilhados
            card_d1, 
            card_d2,
            
            ft.Divider(color="transparent", height=10),
            
            # Lançamento Empilhado
            ft.Container(
                content=ft.Column([
                    txt_valor, 
                    ft.ElevatedButton("Lançar Procedimento", on_click=lancar_procedimento, width=largura_celular, height=45, bgcolor="#00C851", color="#121212")
                ], horizontal_alignment="center", spacing=10),
                bgcolor="#1E1E1E", padding=15, border_radius=10, width=largura_celular
            ),
            
            ft.Divider(color="transparent", height=10),
            ft.Text("Histórico do Caixa", color="#888888", weight="bold"),
            ft.Container(content=lista_historico, border=ft.border.all(1, "#333333"), border_radius=10, padding=10, width=largura_celular),
            
            ft.ElevatedButton("Finalizar o Dia", on_click=ir_para_fechamento, width=largura_celular, height=50, bgcolor="#FFBB33", color="#121212"),
            ft.Divider(color="transparent", height=20),
        ], horizontal_alignment="center")
    )

    # TELA DE FECHAMENTO COM MAPAS INDIVIDUAIS
    lbl_rel_clinica = ft.Text("", size=22, color="#00C851", weight="bold")
    lbl_rel_bruto = ft.Text("", size=14, color="#888888")
    lbl_rel_comissoes = ft.Text("", size=14, color="#FF4444")
    
    lbl_mapa_d1_nome = ft.Text("", size=20, weight="bold", color="white")
    lbl_mapa_d1_qtd = ft.Text("", size=14, color="#888888")
    lbl_mapa_d1_bruto = ft.Text("", size=14, color="#888888")
    lbl_mapa_d1_repasse = ft.Text("", size=16, color="#00ADB5", weight="bold")

    lbl_mapa_d2_nome = ft.Text("", size=20, weight="bold", color="white")
    lbl_mapa_d2_qtd = ft.Text("", size=14, color="#888888")
    lbl_mapa_d2_bruto = ft.Text("", size=14, color="#888888")
    lbl_mapa_d2_repasse = ft.Text("", size=16, color="#00ADB5", weight="bold")

    card_final_d1 = ft.Container(
        content=ft.Column([lbl_mapa_d1_nome, ft.Divider(color="#333333"), lbl_mapa_d1_qtd, lbl_mapa_d1_bruto, lbl_mapa_d1_repasse], horizontal_alignment="center"),
        bgcolor="#1E1E1E", padding=15, border_radius=10, width=largura_celular
    )

    card_final_d2 = ft.Container(
        content=ft.Column([lbl_mapa_d2_nome, ft.Divider(color="#333333"), lbl_mapa_d2_qtd, lbl_mapa_d2_bruto, lbl_mapa_d2_repasse], horizontal_alignment="center"),
        bgcolor="#1E1E1E", padding=15, border_radius=10, width=largura_celular
    )

    painel_fechamento = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Text("Fechamento", size=28, weight="bold", color="#00ADB5"),
            lbl_rel_clinica,
            lbl_rel_bruto, 
            lbl_rel_comissoes,
            ft.Divider(color="transparent", height=10),
            
            card_final_d1, 
            card_final_d2,
            
            ft.Divider(color="transparent", height=20),
            
            ft.Column([
                ft.TextButton("Voltar e Corrigir", on_click=cancelar_fechamento),
                ft.ElevatedButton("Zerar Mapas e Concluir", on_click=resetar_e_voltar, width=largura_celular, bgcolor="#FF4444", color="white", height=50)
            ], horizontal_alignment="center", spacing=10),
            ft.Divider(color="transparent", height=20),
            
        ], horizontal_alignment="center"),
    )

    page.add(painel_config, painel_caixa, painel_fechamento)

ft.app(target=main)
