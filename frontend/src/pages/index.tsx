import { GetServerSideProps } from 'next';

export const getServerSideProps: GetServerSideProps = async () => {
  return {
    redirect: {
      destination: '/support',
      permanent: false,
    },
  };
};

export default function Home() {
  return null;
}
