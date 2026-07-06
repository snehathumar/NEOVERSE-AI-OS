$StartDate = Get-Date -Year 2022 -Month 1 -Day 1
$Rows = 50000

$DataDir = "d:\NEOVERSE AI\data"
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}
$OutputFile = "$DataDir\sales_history.csv"

$Stream = [System.IO.StreamWriter]::new($OutputFile)
$Stream.WriteLine("date,price,quantity_sold,demand,day_of_week,promotion_flag")

$Rand = [System.Random]::new()

for ($i = 0; $i -lt $Rows; $i++) {
    $CurrentDate = $StartDate.AddDays([math]::Floor($i / 50))
    $DayOfWeek = $CurrentDate.DayOfWeek.ToString()
    
    $PromotionFlag = if ($Rand.NextDouble() -lt 0.2) { 1 } else { 0 }
    
    $BasePrice = [math]::Round(($Rand.NextDouble() * 3.0 + 2.5), 2)
    $Price = if ($PromotionFlag -eq 1) { [math]::Round($BasePrice * 0.8, 2) } else { $BasePrice }
    
    $DemandMultiplier = 1.0
    if ($DayOfWeek -eq 'Saturday' -or $DayOfWeek -eq 'Sunday') { $DemandMultiplier *= 1.3 }
    if ($PromotionFlag -eq 1) { $DemandMultiplier *= 1.5 }
    
    # approximate gaussian using Irwin-Hall
    $Gauss = ($Rand.NextDouble() + $Rand.NextDouble() + $Rand.NextDouble() + $Rand.NextDouble() + $Rand.NextDouble() + $Rand.NextDouble() - 3) / 3
    $Demand = [int](100 * $DemandMultiplier + $Gauss * 20)
    if ($Demand -lt 5) { $Demand = 5 }
    
    $QuantitySold = [int]($Demand * ($Rand.NextDouble() * 0.15 + 0.85))
    
    $DateStr = $CurrentDate.ToString("yyyy-MM-dd")
    $Stream.WriteLine("$DateStr,$Price,$QuantitySold,$Demand,$DayOfWeek,$PromotionFlag")
}

$Stream.Close()
Write-Host "Generated 50,000 rows at $OutputFile"
