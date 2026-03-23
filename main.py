import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Gestão Clínica 🦷"
    page.bgcolor = "#121212" 
    page.padding = 10  # Padding reduzido para telas menores
    page.horizontal_alignment = "center"
    # Habilita o scroll na página toda para o HUD não sumir
    page.scroll = ft.ScrollMode.ADAPTIVE 

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

    # --- COMPONENTES VISUAIS ---
    txt_nome_d1 = ft.TextField(label="Nome do Dentista 1", bgcolor="#1E1E1E", border_color="#00ADB5")
    txt_nome_d2 = ft.TextField(label="Nome do Dentista 2", bgcolor="#1E1E1E", border_color="#00ADB5")

    txt_valor = ft.TextField(
        label="Valor (R$)", 
        keyboard_type="number", 
        expand=True, # Agora o campo de texto cresce conforme o espaço
        bgcolor="#1E1E1E", 
        border_color="#00ADB5",
    )
    
    lbl_taxa = ft.Text("Rateio: 15%", size=14, color="#00ADB5", weight="bold")
    lbl_total_bruto = ft.Text("Faturamento Bruto: R$ 0.00", size=14, color="#888888")
    lbl_total_comissoes = ft.Text("Comissões: R$ 0.00", size=14, color="#FF4444")
    lbl_saldo_clinica = ft.Text("Líquido: R$ 0.00", size=20, color="#00C851", weight="bold")
    
    lbl_d1_display = ft.Text("Dentista A", size=16, weight="bold", color="white")
    lbl_d1_saldo_display = ft.Text("R$ 0.00", size=18, weight="bold", color="#00ADB5")
    lbl_d1_status = ft.Text("🟢 Ativo", color="#00C851", size=12)
    
    lbl_d2_display = ft.Text("Dentista B", size=16, weight="bold", color="white")
    lbl_d2_saldo_display = ft.Text("R$ 0.00", size=18, weight="bold", color="#00ADB5")
    lbl_d2_status = ft.Text("🟢 Ativo", color="#00C851", size=12)
    
    lista_historico = ft.ListView(expand=False, spacing=5, height=200)

    # --- LÓGICA ---
    def atualizar_tela():
        ativos = sum([dados["d1_ativo"], dados["d2_ativo"]])
        dados["taxa"] = 0.30 if ativos == 1 else 0.15
        lbl_taxa.value = f"Rateio: {dados['taxa']*100:.0f}%"
        
        lbl_d1_display.value = dados["d1_nome"]
        lbl_d1_saldo_display.value = f"Comissão: R$ {dados['d1_saldo']:.2f}"
        lbl_d1_status.value = f"🟢 Ativo | {dados['d1_qtd']} Atend." if dados["d1_ativo"] else f"🔴 Fechado"
        
        lbl_d2_display.value = dados["d2_nome"]
        lbl_d2_saldo_display.value = f"Comissão: R$ {dados['d2_saldo']:.2f}"
        lbl_d2_status.value = f"🟢 Ativo | {dados['d2_qtd']} Atend." if dados["d2_ativo"] else f"🔴 Fechado"

        total_repasse = dados["d1_saldo"] + dados["d2_saldo"]
        liquido_clinica = dados["total_geral"] - total_repasse
        
        lbl_total_bruto.value = f"Bruto: R$ {dados['total_geral']:.2f}"
        lbl_total_comissoes.value = f"Comissões: R$ {total_repasse:.2f}"
        lbl_saldo_clinica.value = f"Líquido: R$ {liquido_clinica:.2f}"
        
        page.update()

    def sair_doc1(e):
        dados["d1_ativo"] = False
        btn_sair1.visible = False
        atualizar_tela()

    def sair_doc2(e):
        dados["d2_ativo"] = False
        btn_sair2.visible = False
        atualizar_tela()
        
    btn_sair1 = ft.TextButton("Encerrar", on_click=sair_doc1)
    btn_sair2 = ft.TextButton("Encerrar", on_click=sair_doc2)

    def estornar(e):
        reg = e.control.data
        dados["total_geral"] -= reg["valor"]
        if reg["d1_recebeu"]: 
            dados["d1_saldo"] -= reg["comissao"]
            dados["d1_qtd"] -= 1
        if reg["d2_recebeu"]: 
            dados["d2_saldo"] -= reg["comissao"]
            dados["d2_qtd"] -= 1
        lista_historico.controls.remove(reg["ui_row"])
        atualizar_tela()

    def lancar_procedimento(e):
        if not txt_valor.value: return
        try:
            v = float(txt_valor.value.replace(",", "."))
            comissao = v * dados["taxa"]
            dados["total_geral"] += v 
            rec1, rec2 = dados["d1_ativo"], dados["d2_ativo"]
            if rec1: dados["d1_saldo"] += comissao; dados["d1_qtd"] += 1; dados["d1_bruto"] += v
            if rec2: dados["d2_saldo"] += comissao; dados["d2_qtd"] += 1; dados["d2_bruto"] += v
            
            row_ui = ft.Container(
                content=ft.Row([
                    ft.Text(f"R$ {v:.2f}", weight="bold", color="white"),
                    ft.TextButton("Desfazer", data={"valor":v,"comissao":comissao,"d1_recebeu":rec1,"d2_recebeu":rec2}, on_click=estornar)
                ], alignment="spaceBetween"),
                bgcolor="#1E1E1E", padding=10, border_radius=8
            )
            # Adiciona a referência da UI no dicionário do botão para o estorno funcionar
            lista_historico.controls.insert(0, row_ui)
            # Link da UI para remoção
            lista_historico.controls[0].content.controls[1].data["ui_row"] = row_ui

            txt_valor.value = ""; txt_valor.focus(); atualizar_tela()
        except: pass

    def iniciar_clinica(e):
        dados["d1_nome"] = txt_nome_d1.value or "D1"; dados["d2_nome"] = txt_nome_d2.value or "D2"
        painel_config.visible = False; painel_caixa.visible = True; atualizar_tela()

    # --- TELAS ---
    painel_config = ft.Column([
        ft.Text("Gestão Clínica", size=28, weight="bold", color="#00ADB5"),
        txt_nome_d1, txt_nome_d2,
        ft.ElevatedButton("Abrir Caixa", on_click=iniciar_clinica, width=300, height=50, bgcolor="#00ADB5", color="#121212")
    ], horizontal_alignment="center", visible=True)

    painel_caixa = ft.Column([
        ft.Row([ft.Text("Caixa Aberto", size=20, weight="bold", color="#00ADB5"), lbl_taxa], alignment="spaceBetween"),
        ft.Container(
            content=ft.Column([lbl_saldo_clinica, ft.Row([lbl_total_bruto, lbl_total_comissoes], alignment="center", spacing=20)], horizontal_alignment="center"),
            bgcolor="#1E1E1E", padding=10, border_radius=10
        ),
        # ResponsiveRow faz os cards quebrarem linha se não couberem
        ft.ResponsiveRow([
            ft.Container(ft.Column([lbl_d1_display, lbl_d1_saldo_display, lbl_d1_status, btn_sair1], horizontal_alignment="center"), bgcolor="#1E1E1E", padding=10, border_radius=10, col={"xs": 12, "sm": 6}),
            ft.Container(ft.Column([lbl_d2_display, lbl_d2_saldo_display, lbl_d2_status, btn_sair2], horizontal_alignment="center"), bgcolor="#1E1E1E", padding=10, border_radius=10, col={"xs": 12, "sm": 6}),
        ]),
        ft.Row([txt_valor, ft.IconButton(ft.icons.ADD, on_click=lancar_procedimento, bgcolor="#00C851", icon_color="white", height=50)], alignment="center"),
        ft.Text("Histórico:", color="#888888", weight="bold"),
        lista_historico,
        ft.ElevatedButton("Finalizar Dia", on_click=lambda e: page.go("/fim"), width=400, height=50, bgcolor="#FF4444", color="white")
    ], visible=False)

    # Implementação básica de navegação para a tela de fim (substituindo o painel_fechamento anterior)
    def ir_fim(e):
        repasse = dados["d1_saldo"] + dados["d2_saldo"]
        page.clean()
        page.add(ft.Column([
            ft.Text("Resumo Final", size=24, color="#00ADB5", weight="bold"),
            ft.Text(f"Caixa Clínica: R$ {dados['total_geral'] - repasse:.2f}", size=20, color="white"),
            ft.Text(f"{dados['d1_nome']}: R$ {dados['d1_saldo']:.2f}", color="#888888"),
            ft.Text(f"{dados['d2_nome']}: R$ {dados['d2_saldo']:.2f}", color="#888888"),
            ft.ElevatedButton("Novo Turno", on_click=lambda _: page.restart(), bgcolor="#00ADB5", color="black")
        ], horizontal_alignment="center"))

    page.add(painel_config, painel_caixa)

ft.app(target=main)
