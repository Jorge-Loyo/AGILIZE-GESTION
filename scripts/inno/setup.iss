; Agilize Gestion - Instalador
; Genera Setup.exe que instala la app y configura conexion al servidor

#define MyAppName "Agilize Gestion"
#define MyAppVersion "2.2.0"
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

[Files]
; Aplicacion
Source: "..\..\dist\AgilizeGestion\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\AgilizeGestion\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\dist\AgilizeGestion\.env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion
Source: "..\..\scripts\pg_launcher.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\assets\logos\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: pintaskbar
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"

[Tasks]
Name: "pintaskbar"; Description: "Anclar a la barra de tareas"; GroupDescription: "Accesos adicionales:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar Agilize Gestion"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: files; Name: "{app}\.env"

[Code]
var
  ConfigPage: TInputQueryWizardPage;

procedure InitializeWizard();
begin
  ConfigPage := CreateInputQueryPage(wpSelectDir,
    'Configuracion del Servidor',
    'Datos de conexion a la base de datos',
    'Ingresa la IP del servidor y la contrasena de PostgreSQL.' + Chr(13) + Chr(10) +
    'Si no sabes estos datos, consulta al administrador.');
  ConfigPage.Add('IP del servidor:', False);
  ConfigPage.Add('Puerto:', False);
  ConfigPage.Add('Contrasena BD:', True);
  ConfigPage.Values[0] := '100.105.199.110';
  ConfigPage.Values[1] := '5432';
  ConfigPage.Values[2] := 'agilize2025';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvPath: String;
  EnvLines: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    EnvPath := ExpandConstant('{app}\.env');

    SetArrayLength(EnvLines, 12);
    EnvLines[0] := '# Base de Datos';
    EnvLines[1] := 'DB_HOST=' + ConfigPage.Values[0];
    EnvLines[2] := 'DB_PORT=' + ConfigPage.Values[1];
    EnvLines[3] := 'DB_NAME=agilize_gestion';
    EnvLines[4] := 'DB_USER=postgres';
    EnvLines[5] := 'DB_PASSWORD=' + ConfigPage.Values[2];
    EnvLines[6] := '';
    EnvLines[7] := '# Aplicacion';
    EnvLines[8] := 'APP_NAME=Agilize Gestion';
    EnvLines[9] := 'APP_VERSION=2.2.0';
    EnvLines[10] := 'SESSION_TIMEOUT_MINUTES=30';
    EnvLines[11] := 'BCRYPT_ROUNDS=12';

    SaveStringsToUTF8File(EnvPath, EnvLines, False);
  end;
end;
