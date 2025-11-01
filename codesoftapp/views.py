from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Cuenta, Transaccion, ResumenCuentas, Periodo, ManoDeObra, Utilidad, Capital
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db.models import Sum, FloatField, Case, When, F, Value, IntegerField, DecimalField
from decimal import Decimal
from django.db.models.functions import Coalesce


capital_debe_gen = 0
capital_haber_gen = 0

# Vista para la página de inicio
@login_required
def inicio(request):
    
    return render(request, 'index.html')

# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('/')

# Vista para mostrar el catálogo de cuentas
@login_required
def catalogo(request):
    cuentas = Cuenta.objects.all().order_by('codigo')
    return render(request, 'catalogo/catalogo.html', {'cuentas': cuentas})

# Vistas relacionadas con el control de costos
@login_required
def control(request):
    return render(request, 'controlcostos/controlcostos.html')

@login_required
def indirectos(request):
    return render(request, 'controlcostos/indirectos.html')

@login_required
def manoobra(request):
    registros = ManoDeObra.objects.all()
    # Recalcula las sumas totales después de eliminar el empleado
    suma_pago_diario = ManoDeObra.objects.aggregate(Sum('pago_diario'))['pago_diario__sum']
    suma_septimo_dia = ManoDeObra.objects.aggregate(Sum('septimo_dia'))['septimo_dia__sum']
    suma_vacaciones = ManoDeObra.objects.aggregate(Sum('vacaciones'))['vacaciones__sum']
    suma_salario_cancelado = ManoDeObra.objects.aggregate(Sum('salario_cancelado'))['salario_cancelado__sum']
    suma_aguinaldo = ManoDeObra.objects.aggregate(Sum('aguinaldo'))['aguinaldo__sum']
    suma_iss = ManoDeObra.objects.aggregate(Sum('iss'))['iss__sum']
    suma_afp = ManoDeObra.objects.aggregate(Sum('afp'))['afp__sum']
    suma_insaforp = ManoDeObra.objects.aggregate(Sum('insaforp'))['insaforp__sum']
    suma_costo_real = ManoDeObra.objects.aggregate(Sum('costo_real'))['costo_real__sum']
    total = suma_costo_real
    periodos = Periodo.objects.all()
    return render(request, 'controlcostos/manoobra.html', {'registros': registros,
        'suma_pago_diario': suma_pago_diario,
        'suma_septimo_dia': suma_septimo_dia,
        'suma_vacaciones': suma_vacaciones,
        'suma_salario_cancelado': suma_salario_cancelado,
        'suma_aguinaldo': suma_aguinaldo,
        'suma_iss': suma_iss,
        'suma_afp': suma_afp,
        'suma_insaforp': suma_insaforp,
        'suma_costo_real': suma_costo_real,
        'periodos':periodos})

# Vistas relacionadas con los estados financieros
@login_required
def estados(request):
    return render(request, 'estadosfinancieros/estadosfinancieros.html')

@login_required
def comprobacion(request, periodo_id=None):
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo')
        
    periodos = Periodo.objects.all()
    periodo_seleccionado = None
    if periodo_id:
        periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)
        if not periodo_seleccionado:
            periodo_seleccionado = None
    
    consulta = Cuenta.objects.filter(resumen_cuentas__isnull=False, resumen_cuentas__periodo=periodo_seleccionado)
    consulta = consulta.values('codigo', 'nombre', 'resumen_cuentas__debe_total', 'resumen_cuentas__haber_total', 'resumen_cuentas__saldo')
    resultados = []
    suma_debe_total = Decimal(0)  # Inicializa la suma del debe
    suma_haber_total = Decimal(0)  # Inicializa la suma del haber
    
    for cuenta in consulta:
        if '1000' <= cuenta['codigo'] <= '1203':
            cuenta['resumen_cuentas__debe_total'] = cuenta['resumen_cuentas__saldo']
            cuenta['resumen_cuentas__haber_total'] = 0
            if(cuenta['resumen_cuentas__debe_total'] < 0):
                cuenta['resumen_cuentas__haber_total'] = -1* (cuenta['resumen_cuentas__debe_total'])
                cuenta['resumen_cuentas__debe_total'] = 0
            if(cuenta['resumen_cuentas__haber_total'] < 0):
                cuenta['resumen_cuentas__debe_total'] = -1* (cuenta['resumen_cuentas__haber_total'])
                cuenta['resumen_cuentas__haber_total'] = 0

        elif '2101' <= cuenta['codigo'] <= '3102':
            cuenta['resumen_cuentas__haber_total'] = cuenta['resumen_cuentas__saldo']
            cuenta['resumen_cuentas__debe_total'] = 0
            if(cuenta['resumen_cuentas__debe_total'] < 0):
                cuenta['resumen_cuentas__haber_total'] = -1* (cuenta['resumen_cuentas__debe_total'])
                cuenta['resumen_cuentas__debe_total'] = 0
            if(cuenta['resumen_cuentas__haber_total'] < 0):
                cuenta['resumen_cuentas__debe_total'] = -1* (cuenta['resumen_cuentas__haber_total'])
                cuenta['resumen_cuentas__haber_total'] = 0

        elif '4101' <= cuenta['codigo'] <= '4112':
            cuenta['resumen_cuentas__debe_total'] = cuenta['resumen_cuentas__saldo']
            cuenta['resumen_cuentas__haber_total'] = 0
            if(cuenta['resumen_cuentas__debe_total'] < 0):
                cuenta['resumen_cuentas__haber_total'] = -1* (cuenta['resumen_cuentas__debe_total'])
                cuenta['resumen_cuentas__debe_total'] = 0
            if(cuenta['resumen_cuentas__haber_total'] < 0):
                cuenta['resumen_cuentas__debe_total'] = -1* (cuenta['resumen_cuentas__haber_total'])
                cuenta['resumen_cuentas__haber_total'] = 0

        elif '510101' <= cuenta['codigo'] <= '510202':
            cuenta['resumen_cuentas__haber_total'] = cuenta['resumen_cuentas__saldo']
            cuenta['resumen_cuentas__debe_total'] = 0
            if(cuenta['resumen_cuentas__debe_total'] < 0):
                cuenta['resumen_cuentas__haber_total'] = -1* (cuenta['resumen_cuentas__debe_total'])
                cuenta['resumen_cuentas__debe_total'] = 0
            if(cuenta['resumen_cuentas__haber_total'] < 0):
                cuenta['resumen_cuentas__debe_total'] = -1* (cuenta['resumen_cuentas__haber_total'])
                cuenta['resumen_cuentas__haber_total'] = 0
        
        resultados.append(cuenta)
        
        suma_debe_total += cuenta['resumen_cuentas__debe_total']
        suma_haber_total += cuenta['resumen_cuentas__haber_total']
    if(suma_debe_total < 0):
        suma_haber_total = -1*(suma_debe_total)
        suma_debe_total=0

    if(suma_haber_total < 0):
        suma_debe_total = -1*(suma_haber_total)
        suma_haber_total=0
    return render(request, 'estadosfinancieros/comprobacion.html', {
            'resultados': resultados,
            'suma_debe_total': suma_debe_total,
            'suma_haber_total': suma_haber_total,
            'periodos': periodos,
            'periodo_seleccionado': periodo_seleccionado,
        })
    return render(request, 'estadosfinancieros/general.html', {'periodos': periodos})
@login_required
def ajustes(request):
    return render(request, 'estadosfinancieros/ajustes.html')

@login_required
def ajustado(request):
    return render(request, 'estadosfinancieros/ajustado.html')

@login_required
def general(request): 
    cuenta1_debe = 0 
    cuenta1_haber = 0 
    cuenta2_debe = 0 
    cuenta2_haber = 0 
    cuenta3_debe = 0 
    cuenta3_haber = 0 
    cuenta4_debe = 0 
    cuenta4_haber = 0 
    cuenta5_debe = 0 
    cuenta5_haber = 0 
    cuenta6_debe = 0 
    cuenta6_haber = 0 
    cuenta7_debe = 0 
    cuenta7_haber = 0 
    cuenta8_debe = 0 
    cuenta8_haber = 0 
    cuenta9_debe = 0 
    cuenta9_haber = 0 
    cuenta10_debe = 0 
    cuenta10_haber = 0 
    cuenta11_debe = 0 
    cuenta11_haber = 0 
    cuenta12_debe = 0 
    cuenta12_haber = 0 
    cuenta13_debe = 0 
    cuenta13_haber = 0 
    cuenta14_debe = 0 
    cuenta14_haber = 0 
    cuenta15_debe = 0 
    cuenta15_haber = 0 
    cuenta16_debe = 0 
    cuenta16_haber = 0 
    cuenta17_debe = 0 
    cuenta17_haber = 0 
    cuenta18_debe = 0 
    cuenta18_haber = 0 
    cuenta19_debe = 0 
    cuenta19_haber = 0 
    cuenta20_debe = 0 
    cuenta20_haber = 0 
    cuenta21_debe = 0 
    cuenta21_haber = 0 
    cuenta22_debe = 0 
    cuenta22_haber = 0 
    cuenta23_debe = 0 
    cuenta23_haber = 0 
    cuenta24_debe = 0 
    cuenta24_haber = 0 
    debe_total = 0 
    haber_total = 0 
    
    periodos = Periodo.objects.all() 
    if request.method == 'POST': 
        periodo_id = request.POST.get('periodo') 
        if periodo_id: 
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id) 
            
            cuenta1 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110101).first() 
            if cuenta1.saldo < 0: cuenta1_haber = -1 * cuenta1.saldo 
            else: cuenta1_debe = cuenta1.saldo 
            
            cuenta2 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110102).first() #esto hace la consulta a la base de datos para obtener el objeto ResumenCuentas correspondiente al período seleccionado y a la cuenta con ID 110102. if cuenta2.saldo < 0: cuenta2_haber = -1 * cuenta2.saldo else: cuenta2_debe = cuenta2.saldo cuenta3 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110201).first() if cuenta3.saldo < 0: cuenta3_haber = -1 * cuenta3.saldo else: cuenta3_debe = cuenta3.saldo cuenta4 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110202).first() if cuenta4.saldo < 0: cuenta4_haber = -1 * cuenta4.saldo else: cuenta4_debe = cuenta4.saldo cuenta5 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110203).first() if cuenta5.saldo < 0: cuenta5_haber = -1 * cuenta5.saldo else: cuenta5_debe = cuenta5.saldo cuenta6 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=1103).first() if cuenta6.saldo < 0: cuenta6_haber = -1 * cuenta6.saldo else: cuenta6_debe = cuenta6.saldo cuenta7 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=1104).first() if cuenta7.saldo < 0: cuenta7_haber = -1 * cuenta7.saldo else: cuenta7_debe = cuenta7.saldo cuenta8 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110401).first() if cuenta8.saldo < 0: cuenta8_haber = -1 * cuenta8.saldo else: cuenta8_debe = cuenta8.saldo cuenta9 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110402).first() if cuenta9.saldo < 0: cuenta9_haber = -1 * cuenta9.saldo else: cuenta9_debe = cuenta9.saldo cuenta10 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=110403).first() if cuenta10.saldo < 0: cuenta10_haber = -1 * cuenta10.saldo else: cuenta10_debe = cuenta10.saldo cuenta11 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=1105).first() if cuenta11.saldo < 0: cuenta11_haber = -1 * cuenta11.saldo else: cuenta11_debe = cuenta11.saldo cuenta12 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=120101).first() if cuenta12.saldo < 0: cuenta12_haber = -1 * cuenta12.saldo else: cuenta12_debe = cuenta12.saldo cuenta13 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=120102).first() if cuenta13.saldo < 0: cuenta13_haber = -1 * cuenta13.saldo else: cuenta13_debe = cuenta13.saldo cuenta14 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=1202).first() if cuenta14.saldo < 0: cuenta14_haber = -1 * cuenta14.saldo else: cuenta14_debe = cuenta14.saldo cuenta15 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=1203).first() if cuenta15.saldo < 0: cuenta15_haber = -1 * cuenta15.saldo else: cuenta15_debe = cuenta15.saldo cuenta16 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2101).first() if cuenta16.saldo < 0: cuenta16_debe = -1 * cuenta16.saldo else: cuenta16_haber = cuenta16.saldo cuenta17 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2102).first() if cuenta17.saldo < 0: cuenta17_debe = -1 * cuenta17.saldo else: cuenta17_haber = cuenta17.saldo cuenta18 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2103).first() if cuenta18.saldo < 0: cuenta18_debe = -1 * cuenta18.saldo else: cuenta18_haber = cuenta18.saldo cuenta19 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2104).first() if cuenta19.saldo < 0: cuenta19_debe = -1 * cuenta19.saldo else: cuenta19_haber = cuenta19.saldo cuenta20 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2105).first() if cuenta20.saldo < 0: cuenta20_debe = -1 * cuenta20.saldo else: cuenta20_haber = cuenta20.saldo cuenta21 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2201).first() if cuenta21.saldo < 0: cuenta21_debe = -1 * cuenta21.saldo else: cuenta21_haber = cuenta21.saldo cuenta22 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2202).first() if cuenta22.saldo < 0: cuenta22_debe = -1 * cuenta22.saldo else: cuenta22_haber = cuenta22.saldo cuenta23 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2201).first() if cuenta23.saldo < 0: cuenta23_debe = -1 * cuenta23.saldo else: cuenta23_haber = cuenta23.saldo cuenta24 = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=2202).first() if cuenta24.saldo < 0: cuenta24_debe = -1 * cuenta24.saldo else: cuenta24_haber = cuenta24.saldo debe_total = (cuenta1_debe + cuenta2_debe + cuenta3_debe + cuenta4_debe + cuenta5_debe + cuenta6_debe + cuenta7_debe + cuenta8_debe + cuenta9_debe + cuenta10_debe + cuenta11_debe + cuenta12_debe + cuenta13_debe + cuenta14_debe + cuenta15_debe + cuenta16_debe + cuenta17_debe + cuenta18_debe + cuenta19_debe + cuenta20_debe + cuenta21_debe + cuenta22_debe + cuenta23_debe + cuenta24_debe + capital_debe_gen) haber_total = (cuenta1_haber + cuenta2_haber + cuenta3_haber + cuenta4_haber + cuenta5_haber + cuenta6_haber + cuenta7_haber + cuenta8_haber + cuenta9_haber + cuenta10_haber + cuenta11_haber + cuenta12_haber + cuenta13_haber + cuenta14_haber + cuenta15_haber + cuenta16_haber + cuenta17_haber + cuenta18_haber + cuenta19_haber + cuenta20_haber + cuenta21_haber + cuenta22_haber + cuenta23_haber + cuenta24_haber + capital_haber_gen) if periodo_seleccionado: capitales = Capital.objects.filter(periodo=periodo_seleccionado).first() if capitales: valorCapital = capitales.valor_capital return render(request, 'estadosfinancieros/general.html', { 'periodos':periodos, 'cuenta1_debe': cuenta1_debe, 'cuenta1_haber': cuenta1_haber, 'cuenta2_debe': cuenta2_debe, 'cuenta2_haber': cuenta2_haber, 'cuenta3_debe': cuenta3_debe, 'cuenta3_haber': cuenta3_haber, 'cuenta4_debe': cuenta4_debe, 'cuenta4_haber': cuenta4_haber, 'cuenta5_debe': cuenta5_debe, 'cuenta5_haber': cuenta5_haber, 'cuenta6_debe': cuenta6_debe, 'cuenta6_haber': cuenta6_haber, 'cuenta7_debe': cuenta7_debe, 'cuenta7_haber': cuenta7_haber, 'cuenta8_debe': cuenta8_debe, 'cuenta8_haber': cuenta8_haber, 'cuenta9_debe': cuenta9_debe, 'cuenta9_haber': cuenta9_haber, 'cuenta10_debe': cuenta10_debe, 'cuenta10_haber': cuenta10_haber, 'cuenta11_debe': cuenta11_debe, 'cuenta11_haber': cuenta11_haber, 'cuenta12_debe': cuenta12_debe, 'cuenta12_haber': cuenta12_haber, 'cuenta13_debe': cuenta13_debe, 'cuenta13_haber': cuenta13_haber, 'cuenta14_debe': cuenta14_debe, 'cuenta14_haber': cuenta14_haber, 'cuenta15_debe': cuenta15_debe, 'cuenta15_haber': cuenta15_haber, 'cuenta16_debe': cuenta16_debe, 'cuenta16_haber': cuenta16_haber, 'cuenta17_debe': cuenta17_debe, 'cuenta17_haber': cuenta17_haber, 'cuenta18_debe': cuenta18_debe, 'cuenta18_haber': cuenta18_haber, 'cuenta19_debe': cuenta19_debe, 'cuenta19_haber': cuenta19_haber, 'cuenta20_debe': cuenta20_debe, 'cuenta20_haber': cuenta20_haber, 'cuenta21_debe': cuenta21_debe, 'cuenta21_haber': cuenta21_haber, 'cuenta22_debe': cuenta22_debe, 'cuenta22_haber': cuenta22_haber, 'cuenta23_debe': cuenta23_debe, 'cuenta23_haber': cuenta23_haber, 'cuenta24_debe': cuenta24_debe, 'cuenta24_haber': cuenta24_haber, 'capital_debe_gen':capital_debe_gen, 'capital_haber_gen':capital_haber_gen, 'haber_total':haber_total, 'debe_total':debe_total })

@login_required
def resultados(request, periodo_id=None):
    utilidades_debe = 0
    utilidades_haber = 0
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo')
        
    periodos = Periodo.objects.all()
    periodo_seleccionado = None
    
    if periodo_id:
        periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

    consultas = Cuenta.objects.filter(
        resumen_cuentas__isnull=False,
        resumen_cuentas__periodo=periodo_seleccionado,
        codigo__in=['4101', '4102', '4103', '4104', '4105', '4106', '4107', '4108', '4109', '4110', '4111', '4112', '510101', '510102']
    ).annotate(
        debe_total=Coalesce(F('resumen_cuentas__debe_total'), 0),
        haber_total=Coalesce(F('resumen_cuentas__haber_total'), 0)
    )

    ##4101
    suma_debe_total1 = consultas.filter(codigo='4101').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total1 = consultas.filter(codigo='4101').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total1 < 0:
        suma_haber_total1 = -1 * suma_debe_total1
        suma_debe_total1 = Decimal(0)

    if suma_haber_total1 < 0:
        suma_debe_total1 = -1 * suma_haber_total1
        suma_haber_total1 = Decimal(0)

    ### 4102
    suma_debe_total2 = consultas.filter(codigo='4102').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total2 = consultas.filter(codigo='4102').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total2 < 0:
        suma_haber_total2 = -1 * suma_debe_total2
        suma_debe_total2 = Decimal(0)

    if suma_haber_total2 < 0:
        suma_debe_total2 = -1 * suma_haber_total2
        suma_haber_total2 = Decimal(0)

    ## 4103
    suma_debe_total3 = consultas.filter(codigo='4103').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total3 = consultas.filter(codigo='4103').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total3 < 0:
        suma_haber_total3 = -1 * suma_debe_total3
        suma_debe_total3 = Decimal(0)

    if suma_haber_total3 < 0:
        suma_debe_total3 = -1 * suma_haber_total3
        suma_haber_total3 = Decimal(0)

    ## 4104
    suma_debe_total4 = consultas.filter(codigo='4104').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total4 = consultas.filter(codigo='4104').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total4 < 0:
        suma_haber_total4 = -1 * suma_debe_total4
        suma_debe_total4 = Decimal(0)

    if suma_haber_total4 < 0:
        suma_debe_total4 = -1 * suma_haber_total4
        suma_haber_total4 = Decimal(0)

    ## 4105
    suma_debe_total5 = consultas.filter(codigo='4105').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total5 = consultas.filter(codigo='4105').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total5 < 0:
        suma_haber_total5 = -1 * suma_debe_total5
        suma_debe_total5 = Decimal(0)

    if suma_haber_total5 < 0:
        suma_debe_total5 = -1 * suma_haber_total5
        suma_haber_total5 = Decimal(0)

    ## 4106
    suma_debe_total6 = consultas.filter(codigo='4106').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total6 = consultas.filter(codigo='4106').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total6 < 0:
        suma_haber_total6 = -1 * suma_debe_total6
        suma_debe_total6 = Decimal(0)

    if suma_haber_total6 < 0:
        suma_debe_total6 = -1 * suma_haber_total6
        suma_haber_total6 = Decimal(0)

    ## 4107
    suma_debe_total7 = consultas.filter(codigo='4107').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total7 = consultas.filter(codigo='4107').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total7 < 0:
        suma_haber_total7 = -1 * suma_debe_total7
        suma_debe_total7 = Decimal(0)

    if suma_haber_total7 < 0:
        suma_debe_total7 = -1 * suma_haber_total7
        suma_haber_total7 = Decimal(0)

    ## 4108
    suma_debe_total8 = consultas.filter(codigo='4108').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total8 = consultas.filter(codigo='4108').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total8 < 0:
        suma_haber_total8 = -1 * suma_debe_total8
        suma_debe_total8 = Decimal(0)

    if suma_haber_total8 < 0:
        suma_debe_total8 = -1 * suma_haber_total8
        suma_haber_total8 = Decimal(0)
    
    ## 4109
    suma_debe_total9 = consultas.filter(codigo='4109').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total9 = consultas.filter(codigo='4109').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total9 < 0:
        suma_haber_total9 = -1 * suma_debe_total9
        suma_debe_total9 = Decimal(0)

    if suma_haber_total9 < 0:
        suma_debe_total9 = -1 * suma_haber_total9
        suma_haber_total9 = Decimal(0)

    ## 4110
    suma_debe_total10 = consultas.filter(codigo='4110').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total10 = consultas.filter(codigo='4110').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total10 < 0:
        suma_haber_total10 = -1 * suma_debe_total10
        suma_debe_total10 = Decimal(0)

    if suma_haber_total10 < 0:
        suma_debe_total10 = -1 * suma_haber_total10
        suma_haber_total10 = Decimal(0)
    
    ## 4111
    suma_debe_total11 = consultas.filter(codigo='4111').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total11 = consultas.filter(codigo='4111').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total11 < 0:
        suma_haber_total11 = -1 * suma_debe_total11
        suma_debe_total11 = Decimal(0)

    if suma_haber_total11 < 0:
        suma_debe_total11 = -1 * suma_haber_total11
        suma_haber_total11 = Decimal(0)

    ## 4112
    suma_debe_total12 = consultas.filter(codigo='4112').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total12 = consultas.filter(codigo='4112').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total12 < 0:
        suma_haber_total12 = -1 * suma_debe_total12
        suma_debe_total12 = Decimal(0)

    if suma_haber_total12 < 0:
        suma_debe_total12 = -1 * suma_haber_total12
        suma_haber_total12 = Decimal(0)

    ## 510101
    suma_debe_total13 = consultas.filter(codigo='510101').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total13 = consultas.filter(codigo='510101').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total13 < 0:
        suma_haber_total13 = -1 * suma_debe_total13
        suma_debe_total13 = Decimal(0)

    if suma_haber_total13 < 0:
        suma_debe_total13 = -1 * suma_haber_total13
        suma_haber_total13 = Decimal(0)
    
    ## 510102
    suma_debe_total14 = consultas.filter(codigo='510102').aggregate(
        Sum('debe_total', output_field=DecimalField())
    )['debe_total__sum'] or Decimal(0)

    suma_haber_total14 = consultas.filter(codigo='510102').aggregate(
        Sum('haber_total', output_field=DecimalField())
    )['haber_total__sum'] or Decimal(0)

    if suma_debe_total14 < 0:
        suma_haber_total14 = -1 * suma_debe_total14
        suma_debe_total14 = Decimal(0)

    if suma_haber_total14 < 0:
        suma_debe_total14 = -1 * suma_haber_total14
        suma_haber_total14 = Decimal(0)
#### lo demas ############
    suma_debe = (suma_debe_total1 + suma_debe_total2 + suma_debe_total3 + 
                 suma_debe_total4 + suma_debe_total5 + suma_debe_total6 + 
                 suma_debe_total7 + suma_debe_total8 + suma_debe_total9 + 
                 suma_debe_total10 + suma_debe_total11 + suma_debe_total12 + 
                 suma_debe_total13 + suma_debe_total14)
    suma_haber = (suma_haber_total1 + suma_haber_total2 + suma_haber_total3 + 
                  suma_haber_total4 + suma_haber_total5 + suma_haber_total6 +
                  suma_haber_total7 + suma_haber_total8 + suma_haber_total9 +
                  suma_haber_total10 + suma_haber_total11 + suma_haber_total12 +
                  suma_haber_total13 + suma_haber_total14)


#########################
    utilidades_haber = suma_haber - suma_debe

    if periodo_id:
        periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

        # Utiliza get_or_create para crear o actualizar la Utilidad directamente
        utilidad, created = Utilidad.objects.get_or_create(periodo=periodo_seleccionado, defaults={'valor_utilidad': utilidades_haber})

        # Actualiza el valor de utilidad en cualquier caso (nueva o existente)
        utilidad.valor_utilidad = utilidades_haber
        utilidad.save()
    
    utilidades_debe = 0
    if utilidades_haber < 0:
        utilidades_debe = utilidades_haber * -1
        utilidades_haber = 0

    return render(request, 'estadosfinancieros/resultados.html', {
        'suma_debe_total1': suma_debe_total1,
        'suma_haber_total1': suma_haber_total1,
        'suma_debe_total2': suma_debe_total2,
        'suma_haber_total2': suma_haber_total2,
        'suma_debe_total3': suma_debe_total3,
        'suma_haber_total3': suma_haber_total3,
        'suma_debe_total4': suma_debe_total4,
        'suma_haber_total4': suma_haber_total4,
        'suma_debe_total5': suma_debe_total5,
        'suma_haber_total5': suma_haber_total5,
        'suma_debe_total6': suma_debe_total6,
        'suma_haber_total6': suma_haber_total6,
        'suma_debe_total7': suma_debe_total7,
        'suma_haber_total7': suma_haber_total7,
        'suma_debe_total8': suma_debe_total8,
        'suma_haber_total8': suma_haber_total8,
        'suma_debe_total9': suma_debe_total9,
        'suma_haber_total9': suma_haber_total9,
        'suma_debe_total10': suma_debe_total10,
        'suma_haber_total10': suma_haber_total10,
        'suma_debe_total11': suma_debe_total11,
        'suma_haber_total11': suma_haber_total11,
        'suma_debe_total12': suma_debe_total12,
        'suma_haber_total12': suma_haber_total12,
        'suma_debe_total13': suma_debe_total13,
        'suma_haber_total13': suma_haber_total13,
        'suma_debe_total14': suma_debe_total14,
        'suma_haber_total14': suma_haber_total14,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'utilidades_haber': utilidades_haber,
        'utilidades_debe':utilidades_debe,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
    })

@login_required
def capital(request):
    periodos = Periodo.objects.all()
    periodo_seleccionado = None

    utilidades_debe = 0
    utilidades_haber = 0
    capital_debe = 0
    capital_haber = 0

    if request.method == 'POST':
        periodo_id = request.POST.get('periodo')
        if periodo_id:
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

    if periodo_seleccionado:
        utilidades = Utilidad.objects.filter(periodo=periodo_seleccionado).first()
        if utilidades:
            valorUtilidad = utilidades.valor_utilidad
            if valorUtilidad < 0:
                utilidades_debe = -1 *valorUtilidad
            else:
                utilidades_haber = valorUtilidad
        cuentas = ResumenCuentas.objects.filter(periodo=periodo_seleccionado, cuenta_id=3101).first()

        saldo = cuentas.saldo
        if saldo < 0:
            capital_debe = -1 *saldo
        else:
            capital_haber = saldo
    

    capitalNuevo_debe = 0
    capitalNuevo_haber = 0

    if capital_debe > 0 and utilidades_debe > 0:
        capitalNuevo_debe = capital_debe + utilidades_debe
    
    if capital_haber > 0 and utilidades_haber > 0:
        capitalNuevo_haber = capital_haber + utilidades_haber

    if capital_haber > 0 and utilidades_debe > 0:
        if(capital_haber - utilidades_debe) > 0:
            capitalNuevo_haber = capital_haber - utilidades_debe
        else:
            capitalNuevo_debe = -1 * (capital_haber - utilidades_debe)
    
    if capital_debe > 0 and utilidades_haber > 0:
        if(capital_debe - utilidades_haber) > 0:
            capitalNuevo_debe = capital_debe - utilidades_haber
        else:
            capitalNuevo_haber = -1 * (capital_debe - utilidades_haber)
    
    if not capital_debe > 0 and not capital_haber > 0:
        if utilidades_debe > 0:
            capitalNuevo_debe = utilidades_debe
        if utilidades_haber > 0:
            capitalNuevo_haber = utilidades_haber
            
    total_debe = capital_debe + utilidades_debe
    total_haber = capital_haber + utilidades_haber
    global capital_debe_gen
    capital_debe_gen = capitalNuevo_debe
    global capital_haber_gen
    capital_haber_gen = capitalNuevo_haber

    if request.method == 'POST':
        periodo_id = request.POST.get('periodo')

        if periodo_id:
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

            if capitalNuevo_debe > 0:
                capital, created = Capital.objects.get_or_create(periodo=periodo_seleccionado, defaults={'valor_capital': capitalNuevo_debe})
                capital.valor_capital = capitalNuevo_debe
                capital.save()

            if capitalNuevo_haber > 0:
                capital, created = Capital.objects.get_or_create(periodo=periodo_seleccionado, defaults={'valor_capital': capitalNuevo_haber})
                capital.valor_capital = capitalNuevo_haber
                capital.save()

    return render(request, 'estadosfinancieros/capital.html', {
        'periodos': periodos,
        'utilidades_debe': utilidades_debe,
        'utilidades_haber': utilidades_haber,
        'capital_debe':capital_debe,
        'capital_haber': capital_haber,
        'capitalNuevo_debe':capitalNuevo_debe,
        'capitalNuevo_haber':capitalNuevo_haber,
        'total_debe':total_debe,
        'total_haber':total_haber
    })


# Vistas relacionadas con las transacciones
@login_required
def transacciones(request, periodo_id=None):
    periodos = Periodo.objects.all()
    periodo_seleccionado = None

    if periodo_id:
        periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

    if not periodo_seleccionado:
        periodo_seleccionado = None

    transacciones = Transaccion.objects.filter(periodo=periodo_seleccionado).order_by('codigo')
    cuentas = Cuenta.objects.all().order_by('codigo')
    suma_debe = Transaccion.objects.filter(periodo=periodo_seleccionado).aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or Decimal(0)
    suma_haber = Transaccion.objects.filter(periodo=periodo_seleccionado).aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or Decimal(0)
    
    return render(request, 'transacciones/transacciones.html', {
        'cuentas': cuentas,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
    })

@login_required
def agregar_cuenta(request):
    cuentas = Cuenta.objects.all().order_by('codigo')
    error_message = None

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')

        cuenta_existente = Cuenta.objects.filter(Q(codigo=codigo) | Q(nombre=nombre)).first()

        if cuenta_existente:
            error_message = "Una cuenta con el mismo código o nombre ya existe en la base de datos."
        else:
            nueva_cuenta = Cuenta(codigo=codigo, nombre=nombre)
            nueva_cuenta.save()
    
    return render(request, 'catalogo/catalogo.html', {'cuentas': cuentas, 'error_message': error_message})

@login_required
def agregar_transaccion(request, periodo_id=None):
    periodos = Periodo.objects.all()
    periodo_seleccionado = None
    cuentas = Cuenta.objects.all().order_by('codigo')

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        movimiento_debe = request.POST.get('movimiento_debe', 0)
        movimiento_haber = request.POST.get('movimiento_haber', 0)
        periodo_id = request.POST.get('periodo')

        if periodo_id:
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)
        if not periodo_seleccionado:
            periodo_seleccionado = None
        transacciones = Transaccion.objects.filter(periodo_id=periodo_id)
        cuenta = Cuenta.objects.get(codigo=codigo)
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

    suma_debe = Transaccion.objects.filter(periodo=periodo_seleccionado).aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or Decimal(0)
    suma_haber = Transaccion.objects.filter(periodo=periodo_seleccionado).aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or Decimal(0)

    return render(request, 'transacciones/transacciones.html', {
        'transacciones': transacciones,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
        'cuentas':cuentas
    })

def modificar_transaccion(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, pk=transaccion_id)
    
    if request.method == 'POST':
        if 'codigo' in request.POST:
            codigo_cuenta = request.POST['codigo']
            cuenta = Cuenta.objects.get(codigo=codigo_cuenta)  # Encuentra la cuenta con el código proporcionado
            transaccion.codigo = cuenta  # Asigna la cuenta a la transacción
        if 'fecha' in request.POST:
            transaccion.fecha = request.POST['fecha']
        if 'descripcion' in request.POST:
            transaccion.descripcion = request.POST['descripcion']
        if 'movimiento_debe' in request.POST:
            transaccion.movimiento_debe = request.POST['movimiento_debe']
        else:
            transaccion.movimiento_debe = 0
        if 'movimiento_haber' in request.POST:
            transaccion.movimiento_haber = request.POST['movimiento_haber']
        else:
            transaccion.movimiento_haber = 0
        transaccion.save()
    
    periodos = Periodo.objects.all()
    periodo_seleccionado = None

    if request.method == 'POST':
        periodo_id = request.POST.get('periodo-select', 'Ninguno')  # Obtén el ID del período desde el formulario
        if periodo_id != 'Ninguno':
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

    transacciones = Transaccion.objects.filter(periodo=periodo_seleccionado).order_by('fecha')
    suma_debe = transacciones.aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or Decimal(0)
    suma_haber = transacciones.aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or Decimal(0)
    cuentas = Cuenta.objects.all().order_by('codigo')

    return render(request, 'transacciones/transacciones.html', {
        'transaccion': transaccion,
        'transacciones': transacciones,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'cuentas': cuentas,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
    })



@login_required
def eliminar_transaccion(request, transaccion_id):
    transaccion = Transaccion.objects.get(id=transaccion_id)
    transaccion.delete()

    transacciones = Transaccion.objects.filter(periodo=transaccion.periodo).order_by('fecha')
    suma_debe = Transaccion.objects.filter(periodo=transaccion.periodo).aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or Decimal(0)
    suma_haber = Transaccion.objects.filter(periodo=transaccion.periodo).aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or Decimal(0)
    cuentas = Cuenta.objects.all().order_by('codigo')

    return redirect('/transacciones', {
        'transaccion': transaccion,
        'transacciones': transacciones,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'cuentas': cuentas,
    })


@login_required
def libro_mayor(request, periodo_id=None):
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo')
        periodos = Periodo.objects.all()
        periodo_seleccionado = None

        if periodo_id:
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

        if not periodo_seleccionado:
            periodo_seleccionado = None

        consulta = Cuenta.objects.filter(resumen_cuentas__isnull=False, resumen_cuentas__periodo=periodo_seleccionado)
        consulta = consulta.values('codigo', 'nombre', 'resumen_cuentas__debe_total', 'resumen_cuentas__haber_total', 'resumen_cuentas__saldo')
        resultados = consulta.all()
    else:
        periodos = Periodo.objects.all()
        periodo_seleccionado = None

        if periodo_id:
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

        if not periodo_seleccionado:
            periodo_seleccionado = None

        consulta = Cuenta.objects.filter(resumen_cuentas__isnull=False, resumen_cuentas__periodo=periodo_seleccionado)
        consulta = consulta.values('codigo', 'nombre', 'resumen_cuentas__debe_total', 'resumen_cuentas__haber_total', 'resumen_cuentas__saldo')
        resultados = consulta.all()
        resultados = resultados.order_by('codigo')

    return render(request, 'transacciones/libromayor.html', {
        'resultados': resultados,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
    })

@login_required
def crear_periodo(request, periodo_id=None):
    if request.method == 'POST':
        nombre_periodo = request.POST.get('nombre_periodo')

        # Encuentra el último período creado
        ultimo_periodo = Periodo.objects.order_by('-codigo').first()
        nuevo_codigo = 1  # Valor predeterminado si no hay ningún período existente

        if ultimo_periodo:
            # Si hay períodos existentes, incrementa el código en 1
            nuevo_codigo = int(ultimo_periodo.codigo) + 1

        # Convierte nuevo_codigo a una cadena
        nuevo_codigo = str(nuevo_codigo)

        # Crea el nuevo período con el código generado
        nuevo_periodo = Periodo(codigo=nuevo_codigo, nombre=nombre_periodo)
        nuevo_periodo.save()

    periodos = Periodo.objects.all()
    periodo_seleccionado = None

    if periodo_id:
        periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

    if not periodo_seleccionado:
        periodo_seleccionado = None

    transacciones = Transaccion.objects.filter(periodo=periodo_seleccionado).order_by('codigo')
    cuentas = Cuenta.objects.all().order_by('codigo')
    suma_debe = Transaccion.objects.filter(periodo=periodo_seleccionado).aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or Decimal(0)
    suma_haber = Transaccion.objects.filter(periodo=periodo_seleccionado).aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or Decimal(0)
    
    return render(request, 'transacciones/transacciones.html', {
        'transacciones': transacciones,
        'cuentas': cuentas,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
    })



def filtrar_transacciones(request, periodo_id=None):
    periodos = Periodo.objects.all()
    cuentas = Cuenta.objects.all().order_by('codigo')
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo-select')  # Obtén el ID del período desde el formulario
        suma_debe = Transaccion.objects.filter(periodo=periodo_id).aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or Decimal(0)
        suma_haber = Transaccion.objects.filter(periodo=periodo_id).aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or Decimal(0)
        if periodo_id == 'Ninguno':
            # Si se selecciona "Todos los períodos," muestra todas las transacciones
            return render(request, 'transacciones/transacciones.html', {'periodos'})
        else:
            # De lo contrario, filtra las transacciones por el período seleccionado
            transacciones = Transaccion.objects.filter(periodo_id=periodo_id)

        # Aquí puedes realizar cualquier otro procesamiento necesario antes de mostrar las transacciones

        # A continuación, debes pasar las transacciones filtradas a la plantilla
        return render(request, 'transacciones/transacciones.html', 
                      {'transacciones':transacciones, 
                       'suma_debe':suma_debe, 
                       'suma_haber': suma_haber,
                       'suma_haber': suma_haber,
                       'periodos': periodos,
                       'cuentas': cuentas,
                       })


from decimal import Decimal

@login_required
def actualizar_resumen_cuentas(request, periodo_id=None):
    # Lógica para manejar solicitudes POST
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo')
        periodo_seleccionado = None
        if periodo_id:
            periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

        # Obtén todas las cuentas, incluso las que no tienen transacciones
        cuentas = Cuenta.objects.all()

        # Si hay un periodo seleccionado, realiza los cálculos
        if periodo_seleccionado:
            cuentas = cuentas.annotate(
                suma_debe=Sum(
                    Case(
                        When(transaccion__periodo=periodo_seleccionado, then=F('transaccion__movimiento_debe')),
                        default=Value(0, output_field=DecimalField()),  # Establece output_field como DecimalField
                    )
                ),
                suma_haber=Sum(
                    Case(
                        When(transaccion__periodo=periodo_seleccionado, then=F('transaccion__movimiento_haber')),
                        default=Value(0, output_field=DecimalField()),  # Establece output_field como DecimalField
                    )
                )
            )

            ResumenCuentas.objects.filter(periodo=periodo_seleccionado).delete()

            for cuenta in cuentas:
                suma_debe = float(cuenta.suma_debe)
                suma_haber = float(cuenta.suma_haber)
                saldo = 0

                if '1000' <= cuenta.codigo <= '1203':
                    saldo = suma_debe - suma_haber
                elif '2101' <= cuenta.codigo <= '3102':
                    saldo = suma_haber - suma_debe
                elif '4101' <= cuenta.codigo <= '4112':
                    saldo = suma_debe - suma_haber
                elif '510101' <= cuenta.codigo <= '510202':
                    saldo = suma_haber - suma_debe

                ResumenCuentas.objects.update_or_create(
                    periodo=periodo_seleccionado,
                    cuenta=cuenta,
                    defaults={
                        'debe_total': suma_debe,
                        'haber_total': suma_haber,
                        'saldo': saldo,
                    }
                )
    else:
        # Si no hay periodo seleccionado, establece los valores por defecto
        cuentas = cuentas.annotate(
            suma_debe=Value(0, output_field=DecimalField()),  # Establece output_field como DecimalField
            suma_haber=Value(0, output_field=DecimalField())  # Establece output_field como DecimalField
        )
    # Lógica para manejar solicitudes GET
    periodos = Periodo.objects.all()
    periodo_seleccionado = None

    if periodo_id:
        periodo_seleccionado = get_object_or_404(Periodo, pk=periodo_id)

    consulta = Cuenta.objects.filter(
        resumen_cuentas__isnull=False,
        resumen_cuentas__periodo=periodo_seleccionado
    ).values(
        'codigo', 'nombre', 'resumen_cuentas__debe_total',
        'resumen_cuentas__haber_total', 'resumen_cuentas__saldo'
    )

    resultados = consulta.all()

    suma_debe_total = ResumenCuentas.objects.filter(
        periodo=periodo_seleccionado
    ).aggregate(Sum('debe_total'))['debe_total__sum'] or 0

    suma_haber_total = ResumenCuentas.objects.filter(
        periodo=periodo_seleccionado
    ).aggregate(Sum('haber_total'))['haber_total__sum'] or 0

    suma_debe = Transaccion.objects.filter(
        periodo=periodo_seleccionado
    ).aggregate(Sum('movimiento_debe'))['movimiento_debe__sum'] or 0

    suma_haber = Transaccion.objects.filter(
        periodo=periodo_seleccionado
    ).aggregate(Sum('movimiento_haber'))['movimiento_haber__sum'] or 0

    cuentas = cuentas.order_by('codigo')
    transacciones = Transaccion.objects.filter(
        periodo=periodo_seleccionado
    ).order_by('fecha')

    return render(request, 'transacciones/transacciones.html', {
        'resultados': resultados,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
        'transacciones': transacciones,
        'suma_debe': suma_debe,
        'suma_haber': suma_haber,
        'cuentas': cuentas,
        'suma_debe_total': suma_debe_total,
        'suma_haber_total': suma_haber_total,
    })


def agregar_empleado(request):
    if request.method == "POST":
        nombre=request.POST.get('nombre')
        puesto=request.POST.get('puesto')
        salario=float(request.POST.get('salario'))
        
        pago_diario=salario
        septimo=salario*7
        vacaciones=((15*salario)+0.3*(15*salario))/52
        salario_cancelado=septimo + vacaciones
        aguinaldo=(15*salario)/52
        ISS=salario_cancelado*0.075
        AFP=salario_cancelado*0.0875
        INSAFORP=salario*0.01
        costo_real=septimo+vacaciones+aguinaldo+ISS+AFP+INSAFORP

        # Cálculos y creación del nuevo empleado
        nuevo_empleado = ManoDeObra(nombre_empleado=nombre, puesto_trabajo=puesto, pago_diario=pago_diario, septimo_dia=septimo,
                                    vacaciones=vacaciones, salario_cancelado=salario_cancelado, aguinaldo=aguinaldo,
                                    iss=ISS, afp=AFP, insaforp=INSAFORP, costo_real=costo_real)
        nuevo_empleado.save()

    # Recalcula las sumas totales después de agregar el empleado
    suma_pago_diario = ManoDeObra.objects.aggregate(Sum('pago_diario'))['pago_diario__sum']
    suma_septimo_dia = ManoDeObra.objects.aggregate(Sum('septimo_dia'))['septimo_dia__sum']
    suma_vacaciones = ManoDeObra.objects.aggregate(Sum('vacaciones'))['vacaciones__sum']
    suma_salario_cancelado = ManoDeObra.objects.aggregate(Sum('salario_cancelado'))['salario_cancelado__sum']
    suma_aguinaldo = ManoDeObra.objects.aggregate(Sum('aguinaldo'))['aguinaldo__sum']
    suma_iss = ManoDeObra.objects.aggregate(Sum('iss'))['iss__sum']
    suma_afp = ManoDeObra.objects.aggregate(Sum('afp'))['afp__sum']
    suma_insaforp = ManoDeObra.objects.aggregate(Sum('insaforp'))['insaforp__sum']
    suma_costo_real = ManoDeObra.objects.aggregate(Sum('costo_real'))['costo_real__sum']
    total = suma_costo_real

    registros = ManoDeObra.objects.all()
    periodos = Periodo.objects.all()


    return render(request, 'controlcostos/manoobra.html', {
        'registros': registros,
        'suma_pago_diario': suma_pago_diario,
        'suma_septimo_dia': suma_septimo_dia,
        'suma_vacaciones': suma_vacaciones,
        'suma_salario_cancelado': suma_salario_cancelado,
        'suma_aguinaldo': suma_aguinaldo,
        'suma_iss': suma_iss,
        'suma_afp': suma_afp,
        'suma_insaforp': suma_insaforp,
        'suma_costo_real': suma_costo_real,
        'periodos':periodos
    })

def modificar_empleado(request, empleado_id):
    empleado = get_object_or_404(ManoDeObra, pk=empleado_id)

    if request.method == "POST":
        # Obtén los datos actualizados de la solicitud POST
        nombre = request.POST.get('nombre')
        puesto = request.POST.get('puesto')
        salario = float(request.POST.get('salario'))
        # Realiza los cálculos necesarios
        pago_diario = salario
        septimo = salario * 7
        vacaciones = ((15 * salario) + 0.3 * (15 * salario)) / 52
        salario_cancelado = septimo + vacaciones
        aguinaldo = (15 * salario) / 52
        ISS = salario_cancelado * 0.075
        AFP = salario_cancelado * 0.0875
        INSAFORP = salario * 0.01
        costo_real = septimo + vacaciones + aguinaldo + ISS + AFP + INSAFORP

        # Actualiza los campos del empleado con los nuevos valores
        empleado.nombre_empleado = nombre
        empleado.puesto_trabajo = puesto
        empleado.pago_diario = pago_diario
        empleado.septimo_dia = septimo
        empleado.vacaciones = vacaciones
        empleado.salario_cancelado = salario_cancelado
        empleado.aguinaldo = aguinaldo
        empleado.iss = ISS
        empleado.afp = AFP
        empleado.insaforp = INSAFORP
        empleado.costo_real = costo_real

        # Recalcula las sumas totales después de modificar el empleado
        suma_pago_diario = ManoDeObra.objects.aggregate(Sum('pago_diario'))['pago_diario__sum']
        suma_septimo_dia = ManoDeObra.objects.aggregate(Sum('septimo_dia'))['septimo_dia__sum']
        suma_vacaciones = ManoDeObra.objects.aggregate(Sum('vacaciones'))['vacaciones__sum']
        suma_salario_cancelado = ManoDeObra.objects.aggregate(Sum('salario_cancelado'))['salario_cancelado__sum']
        suma_aguinaldo = ManoDeObra.objects.aggregate(Sum('aguinaldo'))['aguinaldo__sum']
        suma_iss = ManoDeObra.objects.aggregate(Sum('iss'))['iss__sum']
        suma_afp = ManoDeObra.objects.aggregate(Sum('afp'))['afp__sum']
        suma_insaforp = ManoDeObra.objects.aggregate(Sum('insaforp'))['insaforp__sum']
        suma_costo_real = ManoDeObra.objects.aggregate(Sum('costo_real'))['costo_real__sum']
        total = suma_costo_real

        empleado.save()

    registros = ManoDeObra.objects.all()
    periodos = Periodo.objects.all()

    return redirect('/mano_de_obra_directa', {
        'registros': registros,
        'suma_pago_diario': suma_pago_diario,
        'suma_septimo_dia': suma_septimo_dia,
        'suma_vacaciones': suma_vacaciones,
        'suma_salario_cancelado': suma_salario_cancelado,
        'suma_aguinaldo': suma_aguinaldo,
        'suma_iss': suma_iss,
        'suma_afp': suma_afp,
        'suma_insaforp': suma_insaforp,
        'suma_costo_real': suma_costo_real,
        'periodos':periodos
    })

def eliminar_empleado(request, empleado_id):
    empleado = get_object_or_404(ManoDeObra, pk=empleado_id)
    empleado.delete()

    # Recalcula las sumas totales después de eliminar el empleado
    suma_pago_diario = ManoDeObra.objects.aggregate(Sum('pago_diario'))['pago_diario__sum']
    suma_septimo_dia = ManoDeObra.objects.aggregate(Sum('septimo_dia'))['septimo_dia__sum']
    suma_vacaciones = ManoDeObra.objects.aggregate(Sum('vacaciones'))['vacaciones__sum']
    suma_salario_cancelado = ManoDeObra.objects.aggregate(Sum('salario_cancelado'))['salario_cancelado__sum']
    suma_aguinaldo = ManoDeObra.objects.aggregate(Sum('aguinaldo'))['aguinaldo__sum']
    suma_iss = ManoDeObra.objects.aggregate(Sum('iss'))['iss__sum']
    suma_afp = ManoDeObra.objects.aggregate(Sum('afp'))['afp__sum']
    suma_insaforp = ManoDeObra.objects.aggregate(Sum('insaforp'))['insaforp__sum']
    suma_costo_real = ManoDeObra.objects.aggregate(Sum('costo_real'))['costo_real__sum']
    total = suma_costo_real

    registros = ManoDeObra.objects.all()
    periodos = Periodo.objects.all()

    return redirect('/mano_de_obra_directa', {
        'registros': registros,
        'suma_pago_diario': suma_pago_diario,
        'suma_septimo_dia': suma_septimo_dia,
        'suma_vacaciones': suma_vacaciones,
        'suma_salario_cancelado': suma_salario_cancelado,
        'suma_aguinaldo': suma_aguinaldo,
        'suma_iss': suma_iss,
        'suma_afp': suma_afp,
        'suma_insaforp': suma_insaforp,
        'suma_costo_real': suma_costo_real,
        'periodos':periodos
    })

def agregar_a_partida_doble(request):
    if request.method == "POST":
        fecha = request.POST.get('fecha')
        periodo = request.POST.get('periodo')
    
        suma_pago_diario = ManoDeObra.objects.aggregate(Sum('pago_diario'))['pago_diario__sum']
        suma_septimo_dia = ManoDeObra.objects.aggregate(Sum('septimo_dia'))['septimo_dia__sum']
        cuenta = Cuenta.objects.get(codigo='4103')
        descripcion = 'Mano de obra directa'
        movimiento_debe = suma_septimo_dia
        movimiento_haber = 0
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        suma_vacaciones = ManoDeObra.objects.aggregate(Sum('vacaciones'))['vacaciones__sum']
        cuenta = Cuenta.objects.get(codigo='4104')
        descripcion = 'Mano de obra directa'
        movimiento_debe = suma_vacaciones
        movimiento_haber = 0
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        suma_salario_cancelado = ManoDeObra.objects.aggregate(Sum('salario_cancelado'))['salario_cancelado__sum']

        suma_aguinaldo = ManoDeObra.objects.aggregate(Sum('aguinaldo'))['aguinaldo__sum']
        cuenta = Cuenta.objects.get(codigo='4105')
        descripcion = 'Mano de obra directa'
        movimiento_debe = suma_aguinaldo
        movimiento_haber = 0
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        suma_iss = ManoDeObra.objects.aggregate(Sum('iss'))['iss__sum']
        cuenta = Cuenta.objects.get(codigo='4106')
        descripcion = 'Mano de obra directa'
        movimiento_debe = suma_iss
        movimiento_haber = 0
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        suma_afp = ManoDeObra.objects.aggregate(Sum('afp'))['afp__sum']
        cuenta = Cuenta.objects.get(codigo='4107')
        descripcion = 'Mano de obra directa'
        movimiento_debe = suma_afp
        movimiento_haber = 0
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        suma_insaforp = ManoDeObra.objects.aggregate(Sum('insaforp'))['insaforp__sum']
        cuenta = Cuenta.objects.get(codigo='4108')
        descripcion = 'Mano de obra directa'
        movimiento_debe = suma_insaforp
        movimiento_haber = 0
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        suma_costo_real = ManoDeObra.objects.aggregate(Sum('costo_real'))['costo_real__sum']
        cuenta = Cuenta.objects.get(codigo='110101')
        descripcion = 'Mano de obra directa'
        movimiento_debe = 0
        movimiento_haber = suma_costo_real
        periodo_id = periodo
        nueva_transaccion = Transaccion(
            codigo=cuenta,
            fecha=fecha,
            descripcion=descripcion,
            movimiento_debe=movimiento_debe,
            movimiento_haber=movimiento_haber,
            periodo_id = periodo_id
        )
        nueva_transaccion.save()

        total = suma_costo_real
    return redirect('/mano_de_obra_directa')
