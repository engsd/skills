# Workspace And Session Examples

## Use Pi in the current project

```powershell
& 'C:\Users\eng\ps1\pi.ps1' start -Alias 'feature-a' -Prompt 'Implement feature A'
```

## Use Pi for another directory

```powershell
& 'C:\Users\eng\ps1\pi.ps1' start -Workspace 'C:\Users\eng\Desktop\other-project' -Alias 'docs-pass' -Prompt 'Write the README'
```

## Continue a named session

```powershell
& 'C:\Users\eng\ps1\pi.ps1' send -Workspace 'C:\Users\eng\Desktop\other-project' -Alias 'docs-pass' -Prompt 'Now add installation steps'
```

## Continue an exact session id

```powershell
& 'C:\Users\eng\ps1\pi.ps1' send -Workspace 'C:\Users\eng\Desktop\other-project' -SessionId '019e...' -Prompt 'Continue from the previous debugging step'
```

## Inspect available sessions before choosing

```powershell
& 'C:\Users\eng\ps1\pi.ps1' list -Workspace 'C:\Users\eng\Desktop\other-project'
```

## Rebind the default session

```powershell
& 'C:\Users\eng\ps1\pi.ps1' use -Workspace 'C:\Users\eng\Desktop\other-project' -SessionId '019e...'
```
