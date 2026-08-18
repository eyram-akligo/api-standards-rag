$containerName = "pgvector-container"

$existing = docker ps -a --filter "name=^$containerName$" --format "{{.Names}}"

if ($existing -eq $containerName) {
    Write-Host "Container already exists. Starting it..."
    docker start $containerName
} else {
    Write-Host "Creating pgvector container..."

    docker run -d `
        --name $containerName `
        -e POSTGRES_USER=myuser `
        -e POSTGRES_PASSWORD=admin `
        -e POSTGRES_DB=ragdb `
        -p 5432:5432 `
        -v pgvector-data:/var/lib/postgresql `
        pgvector/pgvector:pg18
}

Write-Host "pgvector is running."