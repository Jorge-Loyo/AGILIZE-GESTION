; Agilize Gestion - Instalador Profesional
; Inno Setup Script

#define MyAppName "Agilize Gestion"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "Agilize Soluciones"
#define MyAppExeName "AgilizeGestion.exe"

[Setup]
AppId={{A7B3C4D5-E6F7-8901-2345-6789ABCDEF01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={sd}\AgilizeGestion
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist
OutputBaseFilename=Setup_AgilizeGestion_v{#MyAppVersion}
SetupIconFile=..\..\assets\logos\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Types]
Name: "servidor"; Description: "Servidor (instala PostgreSQL + Aplicacion)"
Name: "cliente"; Description: "Cliente (solo Aplicacion, se conecta a un servidor)"

[Components]
Name: "app"; Description: "Agilize Gestion"; Types: servidor cliente; Flags: fixed
Name: "postgres"; Description: "PostgreSQL 16 (base de datos)"; Types: servidor

[Files]
; Aplicacion principal
Source: "..\..\dist\AgilizeGestion\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion; Components: app
Source: "..\..\dist\AgilizeGestion\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: app
Source: "..\..\dist\AgilizeGestion\.env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion; Components: app

; PostgreSQL portable
Source: "..\..\dist\pgsql\*"; DestDir: "{app}\pgsql"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: postgres

; Scripts auxiliares
Source: "..\..\scripts\setup_postgres.py"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: postgres
Source: "..\..\scripts\pg_launcher.py"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: app

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar Agilize Gestion"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c ""{app}\pgsql\bin\pg_ctl.exe"" stop -D ""{app}\pgdata"" -w"; Flags: runhidden; Components: postgres
Filename: "{cmd}"; Parameters: "/c schtasks /delete /tn ""AgilizeGestion_PostgreSQL"" /f"; Flags: runhidden
Filename: "{cmd}"; Parameters: "/c netsh advfirewall firewall delete rule name=""Agilize - PostgreSQL"""; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\pgdata"
Type: filesandordirs; Name: "{app}\pgsql"
Type: filesandordirs; Name: "{app}\logs"
Type: files; Name: "{app}\.env"

[Code]
var
  HostPage: TInputQueryWizardPage;
  PasswordPage: TInputQueryWizardPage;
  ServerHost: String;
  ServerPort: String;
  DBPassword: String;

function CRLF: String;
begin
  Result := Chr(13) + Chr(10);
end;

procedure InitializeWizard();
begin
  HostPage := CreateInputQueryPage(wpSelectComponents,
    'Configuracion de Conexion',
    'Configura la conexion a la base de datos',
    'Ingresa los datos del servidor PostgreSQL:');
  HostPage.Add('Host (IP del servidor):', False);
  HostPage.Add('Puerto:', False);
  HostPage.Values[0] := 'localhost';
  HostPage.Values[1] := '5432';

  PasswordPage := CreateInputQueryPage(HostPage.ID,
    'Contrasena de Base de Datos',
    'Configura la contrasena de PostgreSQL',
    'Esta contrasena se usara para la conexion a la base de datos:');
  PasswordPage.Add('Contrasena:', True);
  PasswordPage.Values[0] := 'agilize2025';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  if (PageID = HostPage.ID) and IsComponentSelected('postgres') then
  begin
    HostPage.Values[0] := 'localhost';
    HostPage.Values[1] := '5432';
    Result := True;
  end;
end;

function InitializePostgreSQL(): Boolean;
var
  ResultCode: Integer;
  AppDir, PgBin, DataDir, PgCtl, InitDB, Psql: String;
  HbaContent, ConfContent: String;
  CmdParams: String;
begin
  Result := True;
  AppDir := ExpandConstant('{app}');
  PgBin := AppDir + '\pgsql\bin';
  DataDir := AppDir + '\pgdata';
  PgCtl := PgBin + '\pg_ctl.exe';
  InitDB := PgBin + '\initdb.exe';
  Psql := PgBin + '\psql.exe';

  // Crear pgdata si no existe
  if not DirExists(DataDir) then
    ForceDirectories(DataDir);

  if not FileExists(DataDir + '\PG_VERSION') then
  begin
    WizardForm.StatusLabel.Caption := 'Inicializando base de datos...';
    // Eliminar contenido de pgdata si quedo basura
    DelTree(DataDir, True, True, True);
    ForceDirectories(DataDir);

    // Ejecutar initdb via cmd para manejar mejor las rutas con espacios
    CmdParams := '/c "' + InitDB + '" -D "' + DataDir + '" -U postgres -E UTF8 --locale=C';
    Exec('cmd.exe', CmdParams, AppDir, SW_HIDE, ewWaitUntilTerminated, ResultCode);
    if ResultCode <> 0 then
    begin
      // Segundo intento sin --locale
      CmdParams := '/c "' + InitDB + '" -D "' + DataDir + '" -U postgres -E UTF8';
      Exec('cmd.exe', CmdParams, AppDir, SW_HIDE, ewWaitUntilTerminated, ResultCode);
      if ResultCode <> 0 then
      begin
        Result := False;
        Exit;
      end;
    end;

    // Configurar para red local
    HbaContent := CRLF + '# Red local - Agilize Gestion' + CRLF +
      'host all all 0.0.0.0/0 md5' + CRLF +
      'host all all ::0/0 md5' + CRLF;
    SaveStringToFile(DataDir + '\pg_hba.conf', HbaContent, True);

    ConfContent := CRLF + '# Agilize Gestion - Red local' + CRLF +
      'listen_addresses = ''*''' + CRLF +
      'port = 5432' + CRLF;
    SaveStringToFile(DataDir + '\postgresql.conf', ConfContent, True);
  end;

  // Iniciar PostgreSQL via cmd
  WizardForm.StatusLabel.Caption := 'Iniciando PostgreSQL...';
  CmdParams := '/c "' + PgCtl + '" start -D "' + DataDir + '" -w -o "-p 5432"';
  Exec('cmd.exe', CmdParams, AppDir, SW_HIDE, ewWaitUntilTerminated, ResultCode);

  // Esperar a que inicie completamente
  Sleep(5000);

  // Setear password (con timeout para que no se cuelgue)
  WizardForm.StatusLabel.Caption := 'Configurando password...';
  CmdParams := '/c set PGPASSWORD=& "' + Psql + '" -U postgres -h localhost -p 5432 -w -c "ALTER USER postgres PASSWORD ''' + DBPassword + ''';"';
  Exec('cmd.exe', CmdParams, AppDir, SW_HIDE, ewWaitUntilTerminated, ResultCode);

  // Crear base de datos
  WizardForm.StatusLabel.Caption := 'Creando base de datos...';
  CmdParams := '/c set PGPASSWORD=& "' + Psql + '" -U postgres -h localhost -p 5432 -w -c "CREATE DATABASE agilize_gestion;"';
  Exec('cmd.exe', CmdParams, AppDir, SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CreateEnvFile();
var
  EnvContent: String;
  EnvPath: String;
  EnvLines: TArrayOfString;
begin
  ServerHost := HostPage.Values[0];
  ServerPort := HostPage.Values[1];
  DBPassword := PasswordPage.Values[0];

  EnvPath := ExpandConstant('{app}\.env');

  // Escribir linea por linea para asegurar encoding limpio
  SetArrayLength(EnvLines, 14);
  EnvLines[0] := '# Base de Datos';
  EnvLines[1] := 'DB_HOST=' + ServerHost;
  EnvLines[2] := 'DB_PORT=' + ServerPort;
  EnvLines[3] := 'DB_NAME=agilize_gestion';
  EnvLines[4] := 'DB_USER=postgres';
  EnvLines[5] := 'DB_PASSWORD=' + DBPassword;
  EnvLines[6] := '';
  EnvLines[7] := '# Aplicacion';
  EnvLines[8] := 'APP_NAME=Agilize Gestion';
  EnvLines[9] := 'APP_VERSION=2.1.0';
  EnvLines[10] := 'SESSION_TIMEOUT_MINUTES=30';
  EnvLines[11] := '';
  EnvLines[12] := '# Seguridad';
  EnvLines[13] := 'SECRET_KEY=agilize_' + GetDateTimeString('yyyymmddhhnnss', '-', ':');

  SaveStringsToUTF8File(EnvPath, EnvLines, False);

  // Agregar BCRYPT_ROUNDS como linea adicional
  SaveStringToFile(EnvPath, 'BCRYPT_ROUNDS=12' + Chr(13) + Chr(10), True);
end;

procedure CreateFirewallRule();
var
  ResultCode: Integer;
begin
  Exec('netsh', 'advfirewall firewall add rule name="Agilize - PostgreSQL" dir=in action=allow protocol=TCP localport=5432',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CreateStartupTask();
var
  ResultCode: Integer;
  PgCtl, DataDir, Cmd: String;
begin
  PgCtl := ExpandConstant('{app}\pgsql\bin\pg_ctl.exe');
  DataDir := ExpandConstant('{app}\pgdata');
  Cmd := '/c schtasks /create /tn "AgilizeGestion_PostgreSQL" /tr "\"' + PgCtl + '\" start -D \"' + DataDir + '\" -w" /sc onlogon /rl highest /f';
  Exec('cmd', Cmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CreateStartBat();
var
  BatContent, BatPath: String;
begin
  BatPath := ExpandConstant('{app}\iniciar_postgres.bat');
  BatContent :=
    '@echo off' + CRLF +
    'echo Iniciando PostgreSQL...' + CRLF +
    '"' + ExpandConstant('{app}\pgsql\bin\pg_ctl.exe') + '" start -D "' + ExpandConstant('{app}\pgdata') + '" -w' + CRLF +
    'echo PostgreSQL iniciado.' + CRLF +
    'pause' + CRLF;
  SaveStringToFile(BatPath, BatContent, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateEnvFile();

    if IsComponentSelected('postgres') then
    begin
      if not InitializePostgreSQL() then
      begin
        MsgBox('Hubo un problema inicializando PostgreSQL.' + Chr(13) + Chr(10) +
               'La aplicacion se instalo correctamente.' + Chr(13) + Chr(10) +
               'Ejecuta "iniciar_postgres.bat" manualmente.', mbInformation, MB_OK);
      end;
      CreateFirewallRule();
      CreateStartupTask();
      CreateStartBat();
    end;
  end;
end;
