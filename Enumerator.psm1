function Get-BasicEnumeration {
    <#
    .DESCRIPTION
    
    This Function will do basic reconaissance for a user. It is meant to speed up the process of gathering information for privilege escalation
    
    .EXAMPLE 
    
    Get-BasicEnumeration
    
    .INPUTS 
    
    N/A
    
    .OUTPUTS
    
    Basic Enumeration details, this includes:
        Users (their enablement)
        Groups Users are in
        Groups on machine
        Hostname
        OS Version
        OS Architecture
        Network Information
        Installed Applications
        Running Processes
    #>
    
    Param(
        [Parameter(Position = 0, Mandatory = $false)][Boolean] $UsersOnly = $false,
        [Parameter(Position = 0, Mandatory = $false)][Boolean] $HostOnly = $false
    )

    # Gather Users on a system
    $Users = Get-LocalUser
    Write-Host -ForegroundColor Cyan "[+] Users"
    foreach ($User in $Users) {
        if ($User.Enabled -eq $True) {
            Write-Host -ForegroundColor Green "`t $User"
        } else {
            Write-Host -ForegroundColor Red "`t $User"
        }
    }
    Write-Host ""

    # Groups on a system
    $Groups = Get-LocalGroup
    Write-Host -ForegroundColor Cyan "[+] Groups"
    foreach ($Group in $Groups) {
        Write-Host -ForegroundColor White "`t $Group"
    }
    Write-Host ""

    # Group Membership (only prints groups with members in them - change with verbosity flag?)
    foreach ($Group in $Groups) {
        if ((Get-LocalGroupMember $Group.Name).count -gt 0) {
            $SubGroup = Get-LocalGroupMember $Group.Name
            Write-Host -ForegroundColor Cyan "[+] Users in $($Group.Name)"
            foreach ($Member in $SubGroup) {
                Write-Host -ForegroundColor White "`t $($Member.Name)" 
            }
            Write-Host ""
        }
    }

    # Machine Information
    Write-Host -ForegroundColor Cyan "[+] Relevant Computer Information"
    $ImportantItems = Get-ComputerInfo | Format-List -Property OsName, OsBuildNumber, OSHotFixes, OsLocalDateTime, OsTimezone, OsInstallDate, OsMuiLanguages, OsArchitecture, LogonServer, CsPartOfDomain
    #Write-Host -ForegroundColor White "`t $ImportantItems"
    $ImportantItems

    # Network Information
    Write-Host -ForegroundColor Cyan "[+] Relevant Network Information"
    Get-NetTCPConnection -State Established, Listen
    Write-Host ""

    # Installed Software
    # This only goes after "Installed Software", and does not technically gather EVERYTHING, though it is cumulative enough
    Write-Host -ForegroundColor Cyan "[+] Installed Software"
    $Software = Get-ChildItem -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ 
    foreach ($Thing in $Software) {
        if ((Get-ItemProperty -Path Registry::$Thing).DisplayName) {
            Write-Host -ForegroundColor Blue "$((Get-ItemProperty -Path Registry::$Thing).DisplayName)"
            Write-Host -ForegroundColor White "`t Install Location: $((Get-ItemProperty -Path Registry::$Thing).InstallLocation)"
            Write-Host -ForegroundColor White "`t Publisher Name:   $((Get-ItemProperty -Path Registry::$Thing).Publisher)"
            Write-Host ""
        } 
    }
    Write-Host ""

    # Processes on machine
    # The -IncludeUserName flag can only be used in an elevated prompt
    Get-Process | Select-Object Id, ProcessName | Sort-Object -Property Id | Format-Table
}
