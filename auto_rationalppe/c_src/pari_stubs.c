/* This file is distributed under the MIT License (see LICENSE). */

#include <pari/pari.h>
#include <assert.h>
#include <stdlib.h>

#define FOR0(i,n) for (i = 0; i < n; i++)

#define FOR1(i,n) for (i = 1; i < n+1; i++)

/* ********************************************************************* */
/* Create new matrix for given dimensions.                               */
/* ********************************************************************* */
long** new_matrix(int ncols, int nrows) {
  long** m;
  int i;
  
  // the matrix is an array of columns  
  m = malloc(ncols * sizeof(long *));
  assert(m != NULL);
  FOR0(i, ncols) {
    // each column is an array of integers
    m[i] = malloc(nrows * sizeof(long));
    assert(m[i] != NULL);
  }
  return m;
}

void free_matrix(long **m, int ncols) {
  int i;
  
  FOR0(i, ncols) {
    free(m[i]);
  }
  free(m);
}

/* ********************************************************************* */
/* Compute the kernel of given matrix, returns NULL for empty kernel and */
/* sets kncols and knrows to the dimensions of the kernel.               */
/* ********************************************************************* */
long** kernel(long **m_arr, int ncols, int nrows, int *kncols_ptr, int *knrows_ptr) {
  pari_sp av;        // stack pointer for garbage collection
  GEN m;             // pari matrix for input
  GEN k;             // pari matrix for kernel
  long **k_arr;      // array for returning kernel
  int i, j;

  av = avma;
  
  // create pari matrix from input
  m = cgetg(ncols+1, t_MAT);
  FOR1(i,ncols) {
    GEN c = cgetg(nrows+1, t_COL);
    gel(m, i) = c;
    FOR1(j,nrows) {
      long e = m_arr[i-1][j-1];
      //printf("i=%i, j=%i: %li\n",i,j,e);
      gel(c,j) = stoi(e);
    }
  }
  
  //printf("The input is:\n");
  //output(m);
  
  k = keri(m);
  //printf("The kernel is:\n");
  //output(k);

  ncols = lg(k) - 1;
  if (ncols == 0) {
    *kncols_ptr = 0;
    k_arr = NULL;
  } else {
    nrows = lg(gel(k,1)) - 1;

    *kncols_ptr = ncols;
    *knrows_ptr = nrows;

    k_arr = new_matrix(ncols, nrows);
    FOR1(i,ncols) {
      GEN c = gel(k,i);
      FOR1(j,nrows) {
        GEN  e = gel(c,j);
        long r = itos(e);
        k_arr[i-1][j-1] = r;
        //printf("i=%i, j=%i: %li\n",i,j,r);
      }
    }
  }

  // collect garbage
  avma = av;
  return k_arr;
  
}

//int test() {
//  long **m;
//  long **k;
//  int ncols = 10;
//  int nrows = 7;
//  int kncols, knrows;
//  int i, j;
//
//  // allocate and initialize matrix
//  m = new_matrix(ncols, nrows);
//  FOR0(i,ncols) {
//    FOR0(j,nrows) {
//      m[i][j] = (i == j ? 1 : 1);
//    }
//  }
//  k = kernel(m, ncols, nrows, &kncols, &knrows);
//  free_matrix(m, ncols);
//  if (k !=  NULL) {
    //printf("nonempty kernel: cols=%i, rows=%i\n", kncols, knrows);
    //  FOR0(i,kncols) {
    //    FOR0(j,knrows) {
    //      printf("i=%i, j=%i: %li\n",i, j, k[i][j]);
    //    }
    //  }
//    free_matrix(k, kncols);
//  } else {
    //printf("empty kernel\n");
//  }
  //printf("done\n");
//  return 0;
//}


//#ifndef NOMAIN
/* ********************************************************************* */
/* Tests the kernel function.                                            */
/* ********************************************************************* */
//int main() {
//  int c;
//  pari_init(10000000,2);
//  FOR0(c,1000000) test();
//}
//#endif








