FROM golang:1.13

WORKDIR /build

COPY . .

RUN go get -d -v github.com/go-sql-driver/mysql
RUN go install -v github.com/go-sql-driver/mysql

RUN go build -o main .

WORKDIR /dist

RUN cp /build/main .

EXPOSE 8887

CMD ["/dist/main", "8887"]