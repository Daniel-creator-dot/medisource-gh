FROM node:24-alpine

WORKDIR /repo

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

COPY package.json package-lock.json ./
COPY apps/marketplace-web/package.json apps/marketplace-web/package.json
COPY packages/ui/package.json packages/ui/package.json
COPY packages/api-client/package.json packages/api-client/package.json
COPY packages/shared-types/package.json packages/shared-types/package.json
COPY packages/design-tokens/package.json packages/design-tokens/package.json

RUN npm ci

COPY packages packages
COPY apps/marketplace-web apps/marketplace-web

RUN npm run build --workspace @medisource/marketplace-web

EXPOSE 3000
CMD ["npm", "run", "start", "--workspace", "@medisource/marketplace-web"]
