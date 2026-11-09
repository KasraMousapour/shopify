FROM node:20-alpine

WORKDIR /app

COPY package.json pnpm-lock.yaml* package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
