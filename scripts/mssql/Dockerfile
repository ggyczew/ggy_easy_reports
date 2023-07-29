FROM mcr.microsoft.com/mssql/server:latest

# Create a config directory
USER root

# Bundle config source
COPY . .

# Grant permissions for to our scripts to be executable
RUN chmod +x entrypoint.sh
RUN chmod +x configure-db.sh

ENTRYPOINT ["./entrypoint.sh"]

# Tail the setup logs to trap the process
CMD ["tail -f /dev/null"]

HEALTHCHECK --interval=15s CMD /opt/mssql-tools/bin/sqlcmd -U sa -P $SA_PASSWORD -Q "select 1" && grep -q "MSSQL CONFIG COMPLETE" ./config.log